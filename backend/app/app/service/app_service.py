from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.account import Account
from app.core.models.app import App, AppVersion, AppVersionStatus
from app.workflows.service.workflow_service import WorkflowService


class AppService:
    @staticmethod
    async def create_system_app(session: AsyncSession, tenant_id: str, model_name: str, model_id: str) -> App:
        """Create a system app for a model."""

        system_account = await Account.get_system_account(session)
        app = App(
            tenant_id=tenant_id,
            name=model_name,
            description=f"System app for {model_name}",
            is_system=True,
            created_by=system_account.id,
            updated_by=system_account.id,
        )
        app.save(session)

        # Create app version
        app_version = AppVersion(
            app_id=app.id,
            version="1.0.0",
            workflow_version="1.0.0",
            published_at=datetime.now(timezone.utc).replace(tzinfo=None),
            published_by=system_account.id,
            status=AppVersionStatus.ACTIVE,
            snapshot=app.snapshot,
        )
        app_version.save(session)
        await WorkflowService.create_system_workflow(
            session, model_id, app.id, model_name, f"System workflow for {model_name}"
        )
        
        return app
