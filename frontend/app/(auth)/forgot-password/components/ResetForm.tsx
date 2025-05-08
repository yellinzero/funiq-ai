'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { passwordValidation } from '@/utils/constants'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import * as z from 'zod'
import { Button } from '@/components/base/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/base/form'
import { Input } from '@/components/base/input'

const resetSchema = z.object({
  code: z.string().length(6, 'auth.code_length'),
  password: passwordValidation,
  confirmPassword: z.string()
    .min(8, 'auth.password_min_length')
}).refine((data: Record<string, string>) => data['password'] === data['confirmPassword'], {
  path: ['confirmPassword'],
  message: 'auth.passwords_dont_match'
})

type ResetFormInputs = z.infer<typeof resetSchema>

interface ResetFormProps {
  onSubmit: (data: ResetFormInputs) => Promise<void>
  countdown: number
  onResend: () => void
}

export default function ResetForm({ onSubmit, countdown, onResend }: ResetFormProps) {
  const { t } = useTranslation(['auth'])

  const form = useForm<ResetFormInputs>({
    resolver: zodResolver(resetSchema),
    defaultValues: { code: '', password: '', confirmPassword: '' },
    mode: 'onChange'
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="code"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('auth.verification_code')}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="text"
                  placeholder={t('auth.enter_code')}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('auth.new_password')}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="password"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('auth.confirm_password')}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="password"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full">
          {t('auth.reset_password')}
        </Button>

        <Button
          type="button"
          variant="ghost"
          disabled={countdown > 0}
          onClick={onResend}
          className="w-full"
        >
          {countdown > 0
            ? t('auth.resend_code_countdown', { seconds: countdown })
            : t('auth.resend_code')}
        </Button>
      </form>
    </Form>
  )
}
