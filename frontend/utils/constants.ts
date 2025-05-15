import * as z from 'zod'

export const SESSION_COOKIE_NAME = 'session'
export const TENANT_HEADER_NAME = 'X-Tenant-ID'

export const passwordValidation = z.string()
  .min(8, 'auth.text.password_min_length')
  .max(64, 'auth.text.password_max_length')
  .regex(/[A-Z]/, 'auth.text.password_uppercase')
  .regex(/[a-z]/, 'auth.text.password_lowercase')
  .regex(/\d/, 'auth.text.password_number')
  .regex(/[!@#$%^&*(),.?":{}|<>]/, 'auth.text.password_special')
