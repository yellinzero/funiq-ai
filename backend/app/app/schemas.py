from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AppBase(BaseModel):
    name: str
    description: str | None = None


class AppCreate(AppBase):
    pass


class AppUpdate(AppBase):
    pass


class AppVersionBase(BaseModel):
    version: str
    workflow_version: str
    status: str
    published_at: datetime
    published_by: str


class AppVersionResponse(AppVersionBase):
    id: str
    app_id: str


class AppResponse(AppBase):
    id: str
    tenant_id: str
    is_system: bool
    version: Optional[str]
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class AppTreeNode(AppResponse):
    versions: List[AppVersionResponse]