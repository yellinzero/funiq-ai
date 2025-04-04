
from pydantic import BaseModel, EmailStr

from app.core.models.account import AccountStatus, TenantUserRole


class TenantCreateRequest(BaseModel):
    name: str


class TenantUpdateRequest(BaseModel):
    name: str


class TenantResponse(BaseModel):
    id: str
    name: str


class UserAddRequest(BaseModel):
    email: EmailStr
    role: TenantUserRole = TenantUserRole.MEMBER


class UserRoleUpdateRequest(BaseModel):
    role: TenantUserRole


class UserResponse(BaseModel):
    id: str
    account_id: str
    tenant_id: str
    role: TenantUserRole


class AccountResponse(BaseModel):
    id: str
    email: str
    name: str
    language: str | None
    status: AccountStatus
    last_login_at: str | None
    last_login_ip: str | None
    role: TenantUserRole | None
    avatar: str | None
