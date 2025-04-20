from typing import List

from fastapi import Request, status
from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.app.schemas import AppUpdate
from app.core.errors import AccountErrorCode, AppErrorCode
from app.core.models.account import Account
from app.core.models.app import App, AppVersion, AppVersionStatus
from app.workflow.service.workflow_service import WorkflowService
from utils.common.datetime import utcnow


class AppService:
    @staticmethod
    async def get_apps(
        session: AsyncSession,
        request: Request
    ) -> List[App]:
        """Get all apps for a tenant"""
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        result = await session.execute(
            select(App)
            .where(App.tenant_id == tenant_id)
            .order_by(App.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_app(
        session: AsyncSession, 
        app_id: str, 
        request: Request
    ) -> App:
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
        
        return app

    @staticmethod
    async def create_app(
        session: AsyncSession,
        name: str,
        description: str,
        request: Request
    ) -> App:
        """Create a new app"""
        tenant_id = request.state.tenant_id
        if not tenant_id:
            raise AccountErrorCode.TENANT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        account_id = request.state.account_id
        if not account_id:
            raise AccountErrorCode.ACCOUNT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Check if the name already exists
        result = await session.execute(
            select(App).where(
                and_(
                    App.tenant_id == tenant_id,
                    App.name == name
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
                name=name,
                description=description,
                is_system=False,
                created_by=account_id,
                updated_by=account_id
            )
            await app.save(session)
            await session.flush()
            
            await WorkflowService.create_workflow(
                session=session,
                app_id=str(app.id),
                name=name,
                description=description,
                request=request
            )
            
            await session.commit()
            await session.refresh(app)
            
            return app
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
    ) -> App:
        """Update app information"""
        app = await AppService.get_app(session, app_id, request)
        
        account_id = request.state.account_id
        if not account_id:
            raise AccountErrorCode.ACCOUNT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )

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
            app.description = app_update.description
            app.updated_by = account_id
            app.updated_at = utcnow().replace(tzinfo=None)
            
            return app
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
    ) -> List[AppVersion]:
        """Get all versions of an app"""
        result = await session.execute(
            select(AppVersion)
            .where(AppVersion.app_id == app_id)
            .order_by(AppVersion.published_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_apps_with_versions(
        session: AsyncSession,
        request: Request
    ) -> List[App]:
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
        return result.scalars().all()
    
    @staticmethod
    async def get_app_version(
        session: AsyncSession,
        app_version_id: str,
    ) -> AppVersion:
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
    ) -> AppVersion:
        """Publish a new version"""
        app = await AppService.get_app(session, app_id, request)
        
        account_id = request.state.account_id
        if not account_id:
            raise AccountErrorCode.ACCOUNT_NOT_FOUND.exception(
                status_code=status.HTTP_404_NOT_FOUND
            )

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
                workflow_id=app.workflow.id,
                workflow_version=workflow_version,
                published_at=utcnow().replace(tzinfo=None),
                published_by=account_id,
                status=AppVersionStatus.ACTIVE,
                snapshot=app.snapshot,
            )
            await app_version.save(session)

            # Update app current version
            app.version = version
            app.updated_by = account_id
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

    @staticmethod
    async def create_system_app(
        session: AsyncSession,
        tenant_id: str,
        model_name: str,
        model_id: str,
        request: Request
    ) -> App:
        """
        Create a system app for a model.

        Args:
            session: Database session
            tenant_id: ID of the tenant
            model_name: Name of the model
            model_id: ID of the model

        Returns:
            App: Created app object

        Raises:
            AppErrorCode.APP_ALREADY_EXISTS: If app with same name exists
            AppErrorCode.APP_CREATE_ERROR: If creation fails
        """
        # Check if app with same name exists
        result = await session.execute(
            select(App).where(
                App.tenant_id == tenant_id,
                App.name == model_name
            )
        )
        if result.scalar_one_or_none():
            raise AppErrorCode.APP_ALREADY_EXISTS.exception(
                data={
                    "tenant_id": tenant_id,
                    "name": model_name,
                    "message": "An app with this name already exists in the tenant"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        system_account = await Account.get_system_account(session)
        
        # Create base app
        app = App(
            tenant_id=tenant_id,
            name=model_name,
            description=f"System app for {model_name}",
            is_system=True,
            version="1.0.0",
            created_by=system_account.id,
            updated_by=system_account.id,
        )
        await app.save(session)

        try:
            # Create system workflow
            workflow = await WorkflowService.create_system_workflow(
                session,
                model_id,
                str(app.id),
                model_name,
                f"System workflow for {model_name}"
            )

            # Publish initial app version
            await AppService.publish_app(
                session,
                app_id=str(app.id),
                version="1.0.0",
                workflow_version=workflow.version,
                request=request
            )
            
            await session.commit()
            await session.refresh(app)

            return app

        except Exception as e:
            logger.error(f"Error creating system app: {e}")
            await session.rollback()
            raise AppErrorCode.APP_CREATE_ERROR.exception(
                data={
                    "tenant_id": tenant_id,
                    "name": model_name,
                    "model_id": model_id,
                    "error": str(e),
                    "message": "Failed to create system app"
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e
