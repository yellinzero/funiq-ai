import * as z from 'zod'

export const passwordValidation = z.string()
  .min(8, { message: 'password_min_length' })
  .max(64, { message: 'password_max_length' })
  .regex(/[A-Z]/, { message: 'password_uppercase' })
  .regex(/[a-z]/, { message: 'password_lowercase' })
  .regex(/[0-9]/, { message: 'password_number' })
  .regex(/[!@#$%^&*(),.?":{}|<>]/, { message: 'password_special' })
