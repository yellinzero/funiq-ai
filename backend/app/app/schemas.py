from datetime import datetime
from typing import List

from pydantic import BaseModel


class AppBase(BaseModel):
    name: str
    description: str | None = None
    support_file: bool | None = None
    support_image: bool | None = None
    support_audio: bool | None = None
    support_thinking: bool | None = None
    support_tool: bool | None = None


class AppCreate(AppBase):
    pass


class AppUpdate(AppBase):
    name: str | None = None


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
    workflow_id: str
    version: str | None = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppTreeNode(AppResponse):
    versions: List[AppVersionResponse]

    class Config:
        from_attributes = True


class AppListResponse(BaseModel):
    items: List[AppResponse]
    total: int

    class Config:
        from_attributes = True


class AppPublishRequest(BaseModel):
    version: str
    workflow_version: str