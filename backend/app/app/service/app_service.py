from typing import List, Tuple

from fastapi import Request, status
from loguru import logger
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func

from app.account.service.tenant_service import TenantService
from app.core.errors import AccountErrorCode, AppErrorCode
from app.core.models.app import App, AppVersion, AppVersionStatus
from app.workflow.service.workflow_service import WorkflowService
from utils.common.datetime import utcnow

from ..schemas import AppCreate, AppResponse, AppTreeNode, AppUpdate, AppVersionResponse


class AppService:
    @staticmethod
    async def get_apps(
        session: AsyncSession,
        request: Request,
        page: int = 1,
        page_size: int = 20,
        search_term: str | None = None,
    ) -> Tuple[List[AppResponse], int]:
        """
        Get all apps for a tenant with pagination and search support.
        """
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Build base query
        query = select(App).where(App.tenant_id == tenant_id)
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
            app_responses.append(AppResponse(
                id=str(app.id),
                tenant_id=str(app.tenant_id),
                workflow_id=str(app.workflow.id),
                name=app.name,
                description=app.description,
                version=app.version,
                support_file=app.support_file,
                support_image=app.support_image,
                support_audio=app.support_audio,
                support_thinking=app.support_thinking,
                support_tool=app.support_tool,
                created_by=str(app.created_by),
                updated_by=str(app.updated_by),
                created_at=app.created_at,
                updated_at=app.updated_at,
            ))
        
        return app_responses, total

    @staticmethod
    async def get_app(
        session: AsyncSession, 
        app_id: str, 
        request: Request
    ) -> AppResponse:
        """Get a single app details"""
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        result = await session.execute(
            select(App).where(
                and_(
                    App.tenant_id == tenant_id,
                    App.id == app_id
                )
            ).options(joinedload(App.workflow))
        )
        
        app = result.scalar_one_or_none()
        if not app:
            raise AppErrorCode.APP_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if not app.workflow:
            raise AppErrorCode.APP_WORKFLOW_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return AppResponse(
            id=str(app.id),
            tenant_id=str(app.tenant_id),
            workflow_id=str(app.workflow.id),
            name=app.name,
            description=app.description,
            version=app.version,
            support_file=app.support_file,
            support_image=app.support_image,
            support_audio=app.support_audio,
            support_thinking=app.support_thinking,
            support_tool=app.support_tool,
            created_by=str(app.created_by),
            updated_by=str(app.updated_by),
            created_at=app.created_at,
            updated_at=app.updated_at,
        )

    @staticmethod
    async def create_application(
        session: AsyncSession,
        app_create: AppCreate,
        request: Request
    ) -> AppResponse:
        """Create a new app"""
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session=session, tenant_id=tenant_id, account_id=account_id)

        # Check if the name already exists
        result = await session.execute(
            select(App).where(
                and_(
                    App.tenant_id == tenant_id,
                    App.name == app_create.name
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
                name=app_create.name,
                description=app_create.description,
                support_file=app_create.support_file,
                support_image=app_create.support_image,
                support_audio=app_create.support_audio,
                support_thinking=app_create.support_thinking,
                support_tool=app_create.support_tool,
                created_by=user.id,
                updated_by=user.id
            )
            await app.save(session)
            await session.flush()
            await WorkflowService.create_workflow(
                session=session,
                app_id=str(app.id),
                name=app_create.name,
                description=app_create.description,
                request=request
            )
            
            await session.commit()
            await session.refresh(app)
            
            return AppResponse(
                id=str(app.id),
                tenant_id=str(app.tenant_id),
                workflow_id=str(app.workflow.id),
                name=app.name,
                description=app.description,
                version=app.version,
                support_file=app.support_file,
                support_image=app.support_image,
                support_audio=app.support_audio,
                support_thinking=app.support_thinking,
                support_tool=app.support_tool,
                created_by=str(app.created_by),
                updated_by=str(app.updated_by),
                created_at=app.created_at,
                updated_at=app.updated_at,
            )
        except Exception as e:
            logger.error(f"Error creating app: {e}")
            await session.rollback()
            raise AppErrorCode.APP_CREATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def update_app(
        session: AsyncSession,
        app_id: str,
        app_update: AppUpdate,
        request: Request
    ) -> AppResponse:
        """Update app information"""
        app = await AppService.get_app(session, app_id, request)
        
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session, app.tenant_id, account_id)

        # Check if new name conflicts with other apps
        if app_update.name != app.name:
            result = await session.execute(
                select(App).where(
                    and_(
                        App.tenant_id == app.tenant_id,
                        App.name == app_update.name,
                        App.id != app_id
                    )
                )
            )
            if result.scalar_one_or_none():
                raise AppErrorCode.APP_ALREADY_EXISTS.exception(
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        try:
            app.name = app_update.name
            if app_update.description:
                app.description = app_update.description
            if app_update.support_file is not None:
                app.support_file = app_update.support_file
            if app_update.support_image is not None:
                app.support_image = app_update.support_image
            if app_update.support_audio is not None:
                app.support_audio = app_update.support_audio
            if app_update.support_thinking is not None:
                app.support_thinking = app_update.support_thinking
            if app_update.support_tool is not None:
                app.support_tool = app_update.support_tool
            app.updated_by = user.id
            app.updated_at = utcnow().replace(tzinfo=None)
            
            await session.commit()
            await session.refresh(app)
            
            return AppResponse(
                id=str(app.id),
                tenant_id=str(app.tenant_id),
                workflow_id=str(app.workflow.id),
                name=app.name,
                description=app.description,
                version=app.version,
                support_file=app.support_file,
                support_image=app.support_image,
                support_audio=app.support_audio,
                support_thinking=app.support_thinking,
                support_tool=app.support_tool,
                created_by=str(app.created_by),
                updated_by=str(app.updated_by),
                created_at=app.created_at,
                updated_at=app.updated_at,
            )
        except Exception as e:
            logger.error(f"Error updating app: {e}")
            await session.rollback()
            raise AppErrorCode.APP_UPDATE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def delete_app(
        session: AsyncSession,
        app_id: str,
        request: Request
    ) -> None:
        """Delete app"""
        app = await AppService.get_app(session, app_id, request)
        
        try:
            await app.delete(session)
        except Exception as e:
            logger.error(f"Error deleting app: {e}")
            await session.rollback()
            raise AppErrorCode.APP_DELETE_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def get_app_versions(
        session: AsyncSession,
        app_id: str,
        request: Request
    ) -> List[AppVersionResponse]:
        """Get all versions of an app"""
        result = await session.execute(
            select(AppVersion)
            .where(AppVersion.app_id == app_id)
            .order_by(AppVersion.published_at.desc())
        )
        versions = result.scalars().all()
        
        version_responses = []
        for version in versions:
            version_responses.append(AppVersionResponse(
                id=str(version.id),
                app_id=str(version.app_id),
                version=version.version,
                workflow_version=version.workflow_version,
                status=version.status,
                published_at=version.published_at,
                published_by=str(version.published_by)
            ))
        
        return version_responses

    @staticmethod
    async def get_apps_with_versions(
        session: AsyncSession,
        request: Request
    ) -> List[AppTreeNode]:
        """Get app tree (includes version information)"""
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        result = await session.execute(
            select(App)
            .where(App.tenant_id == tenant_id)
            .options(joinedload(App.versions))
            .order_by(App.created_at.desc())
        )
        apps = result.scalars().all()
        
        tree_nodes = []
        for app in apps:
            versions = [
                AppVersionResponse(
                    id=str(version.id),
                    app_id=str(version.app_id),
                    version=version.version,
                    workflow_version=version.workflow_version,
                    status=version.status,
                    published_at=version.published_at,
                    published_by=str(version.published_by)
                )
                for version in app.versions
            ]
            
            tree_nodes.append(AppTreeNode(
                id=str(app.id),
                tenant_id=str(app.tenant_id),
                name=app.name,
                description=app.description,
                version=app.version,
                support_file=app.support_file,
                support_image=app.support_image,
                support_audio=app.support_audio,
                support_thinking=app.support_thinking,
                support_tool=app.support_tool,
                created_by=str(app.created_by),
                updated_by=str(app.updated_by),
                created_at=app.created_at,
                updated_at=app.updated_at,
                versions=versions
            ))
        
        return tree_nodes
    
    @staticmethod
    async def get_app_version(
        session: AsyncSession,
        app_version_id: str,
    ) -> AppVersionResponse:
        """Get a single app version details"""
        result = await session.execute(
            select(AppVersion).where(AppVersion.id == app_version_id)
        )
        
        version = result.scalar_one_or_none()
        if not version:
            raise AppErrorCode.APP_VERSION_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return version
    
    @staticmethod
    async def publish_app(
        session: AsyncSession,
        app_id: str,
        version: str,
        workflow_version: str,
        request: Request
    ) -> AppVersionResponse:
        """Publish a new version"""
        app = await AppService.get_app(session, app_id, request)
        
        account_id = request.state.account_id
        user = await TenantService.get_user_by_account_id(session, app.tenant_id, account_id)

        # Check if version already exists
        result = await session.execute(
            select(AppVersion).where(
                and_(
                    AppVersion.app_id == app_id,
                    AppVersion.version == version
                )
            )
        )
        if result.scalar_one_or_none():
            raise AppErrorCode.APP_VERSION_ALREADY_EXISTS.exception(
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create new version
            app_version = AppVersion(
                app_id=app_id,
                version=version,
                workflow_id=app.workflow_id,
                workflow_version=workflow_version,
                published_at=utcnow().replace(tzinfo=None),
                published_by=user.id,
                status=AppVersionStatus.ACTIVE,
                snapshot={
                    "name": app.name,
                    "description": app.description,
                    "support_file": app.support_file,
                    "support_image": app.support_image,
                    "support_audio": app.support_audio,
                    "support_thinking": app.support_thinking,
                    "support_tool": app.support_tool,
                },
            )
            await app_version.save(session)

            # Update app current version
            app.version = version
            app.updated_by = user.id
            app.updated_at = utcnow().replace(tzinfo=None)
            
            await session.commit()
            await session.refresh(app)
            
            return app_version
        except Exception as e:
            logger.error(f"Error publishing app version: {e}")
            await session.rollback()
            raise AppErrorCode.APP_VERSION_PUBLISH_ERROR.exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e