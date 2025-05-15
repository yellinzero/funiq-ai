import type { components } from '@/types/openapi'

type IComponentsSchemas = components['schemas']

// Login related
export type ILoginRequest = IComponentsSchemas['LoginRequest']
export type ILoginResponse = IComponentsSchemas['LoginResponse']

// Signup related
export type ISignupRequest = IComponentsSchemas['SignupRequest']
export type ISignupResponse = IComponentsSchemas['SignupResponse']
export type ISignupVerifyRequest = IComponentsSchemas['SignupVerifyRequest']
export type ISignupVerifyResponse = IComponentsSchemas['SignupVerifyResponse']

// Password related
export type IForgotPasswordRequest = IComponentsSchemas['ForgotPasswordRequest']
export type IForgotPasswordResponse = IComponentsSchemas['ForgotPasswordResponse']
export type IResetPasswordRequest = IComponentsSchemas['ResetPasswordRequest']

// Verification code related
export type IResendVerificationCodeRequest = IComponentsSchemas['ResendVerificationCodeRequest']
export type IResendVerificationCodeResponse = IComponentsSchemas['ResendVerificationCodeResponse']
