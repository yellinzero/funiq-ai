from fastapi import APIRouter, Request, Response
from fastapi_async_sqlalchemy import db
from loguru import logger

from app.account.service.account_service import AccountService
from app.core.schemas import ResponseModel
from utils.security import (
    delete_refresh_token_from_cookie,
    get_refresh_token_from_cookie,
    invalidate_refresh_token,
    set_refresh_token_to_cookie,
)

from .schemas import (
    ActivateAccountRequest,
    ActivateAccountResponse,
    ActivateAccountVerifyRequest,
    ActivateAccountVerifyResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    ResendVerificationCodeRequest,
    ResendVerificationCodeResponse,
    ResetPasswordRequest,
    SignupRequest,
    SignupResponse,
    SignupVerifyRequest,
    SignupVerifyResponse,
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/signup", response_model=ResponseModel[SignupResponse])
async def signup(payload: SignupRequest, request: Request):
    """Register a new account"""
    token = await AccountService.signup(db.session, payload, request)
    return ResponseModel(data={"token": token})


@auth_router.post("/login", response_model=ResponseModel[LoginResponse])
async def login(payload: LoginRequest, request: Request, response: Response):
    """Login with email and password"""
    access_token, refresh_token, tenant_id = await AccountService.login(db.session, payload, request)
    set_refresh_token_to_cookie(response, refresh_token)
    return ResponseModel(data={"access_token": access_token, "tenant_id": tenant_id})


@auth_router.post("/signup-verify", response_model=ResponseModel[SignupVerifyResponse])
async def signup_verify(payload: SignupVerifyRequest, request: Request, response: Response):
    """Verify signup email with verification code"""
    access_token, refresh_token, tenant_id = await AccountService.sign_up_email_verify(db.session, payload, request)
    set_refresh_token_to_cookie(response, refresh_token)
    return ResponseModel(data={"access_token": access_token, "tenant_id": tenant_id})


@auth_router.post("/activate-account", response_model=ResponseModel[ActivateAccountResponse])
async def activate_account(payload: ActivateAccountRequest, request: Request):
    """Send activation email for inactive account"""
    token = await AccountService.activate_account(db.session, payload, request)
    return ResponseModel(data={"token": token})


@auth_router.post("/forgot-password", response_model=ResponseModel[ForgotPasswordResponse])
async def forgot_password(payload: ForgotPasswordRequest, request: Request):
    """Send password reset email"""
    token = await AccountService.send_reset_password_email(db.session, payload, request)
    return ResponseModel(data={"token": token})


@auth_router.post("/reset-password", response_model=ResponseModel[None])
async def reset_password(payload: ResetPasswordRequest):
    """Reset password with verification code"""
    await AccountService.reset_password(db.session, payload)
    return ResponseModel(data=None)


@auth_router.post("/resend-verification-code", response_model=ResponseModel[ResendVerificationCodeResponse])
async def resend_verification_code(payload: ResendVerificationCodeRequest, request: Request):
    """Resend verification code for signup/activation/password reset"""
    token = await AccountService.resend_verification_code(db.session, payload.email, payload.code_type, request)
    return ResponseModel(data={"token": token})


@auth_router.post("/activate-account-verify", response_model=ResponseModel[ActivateAccountVerifyResponse])
async def activate_account_verify(payload: ActivateAccountVerifyRequest, request: Request, response: Response):
    """Verify account activation with verification code"""
    access_token, refresh_token, tenant_id = await AccountService.activate_account_verify(db.session, payload, request)
    set_refresh_token_to_cookie(response, refresh_token)
    return ResponseModel(data={"access_token": access_token, "refresh_token": refresh_token, "tenant_id": tenant_id})


@auth_router.post("/logout", response_model=ResponseModel[None])
async def logout(request: Request, response: Response):
    """Logout current user and invalidate their refresh token"""
    refresh_token = get_refresh_token_from_cookie(request)
    logger.info("Processing logout request")
    if refresh_token:
        invalidate_refresh_token(refresh_token=refresh_token)
        delete_refresh_token_from_cookie(response)
        logger.info("User logged out successfully")
    else:
        logger.info("Logout requested with no refresh token")
    return ResponseModel(data=None)
