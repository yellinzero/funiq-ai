import { type ExtractBodyType, fetchApi } from '@/apis/core'
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

export async function loginApi(body: ExtractBodyType<'post', typeof loginUrl>) {
  return await fetchApi.POST(loginUrl, { body })
}

export async function signupApi(body: ExtractBodyType<'post', typeof signupUrl>) {
  return await fetchApi.POST(signupUrl, { body })
}

export async function signupVerifyApi(body: ExtractBodyType<'post', typeof signupVerifyUrl>) {
  return await fetchApi.POST(signupVerifyUrl, { body })
}

export async function activateAccountApi(body: ExtractBodyType<'post', typeof activateAccountUrl>) {
  return await fetchApi.POST(activateAccountUrl, { body })
}

export async function activateAccountVerifyApi(body: ExtractBodyType<'post', typeof activateAccountVerifyUrl>) {
  return await fetchApi.POST(activateAccountVerifyUrl, { body })
}

export async function forgotPasswordApi(body: ExtractBodyType<'post', typeof forgotPasswordUrl>) {
  return await fetchApi.POST(forgotPasswordUrl, { body })
}

export async function resetPasswordApi(body: ExtractBodyType<'post', typeof resetPasswordUrl>) {
  return await fetchApi.POST(resetPasswordUrl, { body })
}

export async function resendVerificationCodeApi(body: ExtractBodyType<'post', typeof resendVerificationCodeUrl>) {
  return await fetchApi.POST(resendVerificationCodeUrl, { body })
}

export async function logoutApi() {
  return await fetchApi.POST(logoutUrl)
}
