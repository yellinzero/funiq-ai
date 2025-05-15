import type {
  IActivateAccountRequest,
  IActivateAccountVerifyRequest,
  IForgotPasswordRequest,
  ILoginRequest,
  IResendVerificationCodeRequest,
  IResetPasswordRequest,
  ISignupRequest,
  ISignupVerifyRequest,
} from '@/apis/types'
import { fetchApi } from '@/apis/core'
import {
  activateAccountUrl,
  activateAccountVerifyUrl,
  forgotPasswordUrl,
  loginUrl,
  logoutUrl,
  resendVerificationCodeUrl,
  resetPasswordUrl,
  signupUrl,
  signupVerifyUrl,
} from '@/apis/paths'

export async function loginApi(body: ILoginRequest) {
  return await fetchApi.POST(loginUrl, { body })
}

export async function signupApi(body: ISignupRequest) {
  return await fetchApi.POST(signupUrl, { body })
}

export async function signupVerifyApi(body: ISignupVerifyRequest) {
  return await fetchApi.POST(signupVerifyUrl, { body })
}

export async function activateAccountApi(body: IActivateAccountRequest) {
  return await fetchApi.POST(activateAccountUrl, { body })
}

export async function activateAccountVerifyApi(body: IActivateAccountVerifyRequest) {
  return await fetchApi.POST(activateAccountVerifyUrl, { body })
}

export async function forgotPasswordApi(body: IForgotPasswordRequest) {
  return await fetchApi.POST(forgotPasswordUrl, { body })
}

export async function resetPasswordApi(body: IResetPasswordRequest) {
  return await fetchApi.POST(resetPasswordUrl, { body })
}

export async function resendVerificationCodeApi(body: IResendVerificationCodeRequest) {
  return await fetchApi.POST(resendVerificationCodeUrl, { body })
}

export async function logoutApi() {
  return await fetchApi.POST(logoutUrl)
}
