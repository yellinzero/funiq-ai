from typing import Tuple

from fastapi import Request, status
from loguru import logger
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.account.service.tenant_service import TenantService
from app.core.errors import AppErrorCode
from app.core.models.app import App
from app.workflow.schemas import CreateWorkflowRequest
from app.workflow.service.workflow_service import WorkflowService

from ..schemas import AppInfo, AppListResponse, CreateAppRequest, UpdateAppRequest


class AppService:
    @staticmethod
    def app_to_info(app: App) -> AppInfo:
        return AppInfo(**app.to_dict(convert_uuid_to_str=True))

    @staticmethod
    async def get_apps(
        session: AsyncSession,
        request: Request,
        page: int = 1,
        page_size: int = 20,
        search_term: str | None = None,
    ) -> Tuple[AppListResponse, int]:
        """

        Get all apps for a tenant with pagination and search support.
        """
        tenant_id = request.state.tenant_id
        
        try: 
            # Build base query
            query = select(App).where(App.tenant_id == tenant_id).order_by(App.created_at.desc())
            count_query = select(func.count()).select_from(App).where(App.tenant_id == tenant_id)
            
            # Add search condition if provided
            if search_term:
                search_filter = or_(
                    App.name.ilike(f"%{search_term}%"),
                    App.description.ilike(f"%{search_term}%")
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Get total count
            total_result = await session.execute(count_query)
            total = total_result.scalar_one()
            
            # Add pagination and ordering
            offset = (page - 1) * page_size
            query = (
                query
                .order_by(App.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            # Execute query
            result = await session.execute(query)
            apps = result.scalars().all()
            
            # Convert to response objects
            app_responses = []
            for app in apps:
                app_responses.append(AppService.app_to_info(app))
            
            return app_responses, total
        except Exception as e:
            logger.error(f"Error fetching apps: {e}")
            raise AppErrorCode.APP_FETCH_FAILED.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_app(
        session: AsyncSession, 
        app_id: str, 
        request: Request
    ) -> App:
        """Get a single app details"""
        tenant_id = request.state.tenant_id
        
        result = await session.execute(
            select(App).where(
                and_(
                    App.tenant_id == tenant_id,
                    App.id == app_id
                )
            )
        )
        app = result.scalar_one_or_none()
        if not app:
            raise AppErrorCode.APP_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return app

    @staticmethod
    async def create_app(
        session: AsyncSession,
        payload: CreateAppRequest,
        request: Request
    ) -> AppInfo:
        """Create a new app"""
        tenant_id, _, user = await TenantService.get_tenant_and_user(session=session, request=request)

        # Check if the name already exists
        result = await session.execute(
            select(App).where(
                and_(
                    App.tenant_id == tenant_id,
                    App.name == payload.name
                )
            )
        )
        if result.scalar_one_or_none():
            raise AppErrorCode.APP_ALREADY_EXISTS.exception(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            app = App(
                tenant_id=tenant_id,
                name=payload.name,
                description=payload.description,
                created_by=user.id,
                updated_by=user.id
            )
            await app.save(session)
            await session.flush()
            workflow = await WorkflowService.create_workflow(
                session=session,
                request=request,
                payload=CreateWorkflowRequest(
                    app_id=str(app.id),
                ),
                commit=False
            )
            
            app.workflow_id = workflow.id
            await app.save(session)
            app_info = AppService.app_to_info(app)
            await session.commit()
            
            return app_info
        except Exception as e:
            logger.error(f"Error creating app: {e}")
            await session.rollback()
            raise AppErrorCode.APP_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def update_app(
        session: AsyncSession,
        app_id: str,
        payload: UpdateAppRequest,
        request: Request
    ) -> AppInfo:
        """Update app information"""
        app = await AppService.get_app(session=session, app_id=app_id, request=request)
        _, _, user = await TenantService.get_tenant_and_user(session=session, request=request)

        # Check if new name conflicts with other apps
        if payload.name != app.name:
            result = await session.execute(
                select(App).where(
                    and_(
                        App.tenant_id == app.tenant_id,
                        App.name == payload.name,
                        App.id != app_id
                    )
                )
            )
            if result.scalar_one_or_none():
                raise AppErrorCode.APP_ALREADY_EXISTS.exception(
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        try:
            if payload.name:
                app.name = payload.name
            if payload.description:
                app.description = payload.description
            app.updated_by = user.id
            await app.save(session)
            await session.flush()
            app_info = AppService.app_to_info(app)
            await session.commit()
            
            return app_info
        except Exception as e:
            logger.error(f"Error updating app: {e}")
            await session.rollback()
            raise AppErrorCode.APP_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

    @staticmethod
    async def delete_app(
        session: AsyncSession,
        app_id: str,
        request: Request
    ) -> None:
        """Delete app"""
        app = await AppService.get_app(session=session, app_id=app_id, request=request)
        
        try:
            await app.delete(session)
            await session.commit()
        except Exception as e:
            logger.error(f"Error deleting app: {e}")
            await session.rollback()
            raise AppErrorCode.APP_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e