from datetime import datetime, timezone

from fastapi import status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppErrorCode
from app.core.models.account import Account
from app.core.models.app import App, AppVersion, AppVersionStatus
from app.workflows.service.workflow_service import WorkflowService


class AppService:
    @staticmethod
    async def publish_app(
        session: AsyncSession,
        app_id: str,
        version: str,
        workflow_version: str,
        published_by: str,
    ) -> AppVersion:
        """
        Publish a new version of an app.

        Args:
            session: Database session
            app_id: ID of the app to publish
            version: Version string for the app (e.g., "1.0.0")
            workflow_version: Associated workflow version
            published_by: ID of the user publishing the version

        Returns:
            AppVersion: Created app version object

        Raises:
            AppErrorCode.APP_NOT_FOUND: If app doesn't exist
            AppErrorCode.APP_VERSION_ALREADY_EXISTS: If version already exists
            AppErrorCode.APP_VERSION_PUBLISH_ERROR: If publishing fails
        """
        # Check if app exists
        result = await session.execute(
            select(App).where(App.id == app_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            raise AppErrorCode.APP_NOT_FOUND.exception(
                data={
                    "app_id": str(app_id),
                    "message": "Unable to find app for version publishing"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Check if version already exists
        result = await session.execute(
            select(AppVersion).where(
                AppVersion.app_id == app_id,
                AppVersion.version == version
            )
        )
        existing_version = result.scalar_one_or_none()
        if existing_version:
            raise AppErrorCode.APP_VERSION_ALREADY_EXISTS.exception(
                data={
                    "app_id": str(app_id),
                    "version": version,
                    "message": "This version number is already in use"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create new app version
            app_version = AppVersion(
                app_id=app_id,
                version=version,
                workflow_version=workflow_version,
                published_at=datetime.now(timezone.utc).replace(tzinfo=None),
                published_by=published_by,
                status=AppVersionStatus.ACTIVE,
                snapshot=app.snapshot,
            )
            await app_version.save(session)

            # Update app's current version
            app.version = version
            await app.save(session)

            # Commit all changes
            await session.commit()

            logger.info(
                f"Published app version {version} for app {app_id} "
                f"with workflow version {workflow_version}"
            )

            return app_version

        except Exception as e:
            logger.error(f"Error publishing app version: {e}")
            await session.rollback()
            raise AppErrorCode.APP_VERSION_PUBLISH_ERROR.exception(
                data={
                    "app_id": str(app_id),
                    "version": version,
                    "workflow_version": workflow_version,
                    "error": str(e),
                    "message": "Failed to publish app version"
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e

    @staticmethod
    async def create_system_app(
        session: AsyncSession,
        tenant_id: str,
        model_name: str,
        model_id: str
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
                published_by=str(system_account.id)
            )

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
