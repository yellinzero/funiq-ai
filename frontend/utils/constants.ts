export const SESSION_COOKIE_NAME = 'session'
export const THEME_COOKIE_NAME = 'theme'
export const TENANT_HEADER_NAME = 'X-Tenant-ID'

import * as z from 'zod'

export const passwordValidation = z.string()
  .min(8, 'auth.password_min_length')
  .max(64, 'auth.password_max_length')
  .regex(/[A-Z]/, 'auth.password_uppercase')
  .regex(/[a-z]/, 'auth.password_lowercase')
  .regex(/[0-9]/, 'auth.password_number')
  .regex(/[!@#$%^&*(),.?":{}|<>]/, 'auth.password_special')
