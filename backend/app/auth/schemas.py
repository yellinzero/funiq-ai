from pydantic import BaseModel, EmailStr

from app.core.models.account import OAuthProviderName
from utils.security import (
    AccountTokenType,
    PasswordMixin,
)


class SignupRequest(PasswordMixin, BaseModel):
    name: str
    email: EmailStr
    password: str
    invite_code: str | None = None


class ActivateAccountRequest(BaseModel):
    email: str


class SignupVerifyRequest(BaseModel):
    token: str
    code: str


class LoginRequest(PasswordMixin, BaseModel):
    email: EmailStr
    password: str


class SignupResponse(BaseModel):
    token: str


class ActivateAccountResponse(BaseModel):
    token: str


class LoginResponse(BaseModel):
    access_token: str
    tenant_id: str | None
    token_type: str = "bearer"


class SignupVerifyResponse(BaseModel):
    access_token: str
    tenant_id: str | None
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    token: str


class ResetPasswordRequest(PasswordMixin, BaseModel):
    token: str
    code: str
    new_password: str


class ResendVerificationCodeRequest(BaseModel):
    email: EmailStr
    code_type: AccountTokenType


class ResendVerificationCodeResponse(BaseModel):
    token: str


class ActivateAccountVerifyRequest(BaseModel):
    token: str
    code: str


class ActivateAccountVerifyResponse(BaseModel):
    access_token: str
    tenant_id: str | None
    token_type: str = "bearer"


class OAuthLoginRequest(BaseModel):
    provider: OAuthProviderName
    provider_user_id: str
    email: EmailStr
    name: str
    access_token: str
    refresh_token: str | None = None
    profile_data: dict | None = None
    invite_code: str | None = None


class OAuthLoginResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    tenant_id: str | None = None
    token_type: str = "bearer"
