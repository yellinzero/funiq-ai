'use client'

import { useTranslation } from 'react-i18next'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/base/button'
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from '@/components/base/input-otp'
import { REGEXP_ONLY_DIGITS } from 'input-otp'
import { Form, FormControl, FormField, FormItem, FormMessage } from '@/components/base/form'

interface VerificationCodeFormProps {
  onSubmit: (code: string) => Promise<void>
  submitButtonText?: string
  countdown: number
  onResend: () => void
  errorMessage?: string
}

const verificationCodeSchema = z.object({
  code: z.string().length(6, 'auth.code_length'),
})

type VerificationCodeFormInputs = z.infer<typeof verificationCodeSchema>

export default function VerificationCodeForm({
  onSubmit,
  submitButtonText,
  countdown,
  onResend,
  errorMessage,
}: VerificationCodeFormProps) {
  const { t } = useTranslation(['auth'])

  const form = useForm<VerificationCodeFormInputs>({
    resolver: zodResolver(verificationCodeSchema),
    defaultValues: {
      code: '',
    },
  })

  const handleFormSubmit = async (data: VerificationCodeFormInputs) => {
    try {
      await onSubmit(data.code)
    }
    catch (e) {
      console.error('Verification error:', e)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleFormSubmit)} className="flex flex-col gap-4 w-full items-center">
        <FormField
          control={form.control}
          name="code"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <InputOTP
                  maxLength={6}
                  {...field}
                  pattern={REGEXP_ONLY_DIGITS}
                >
                  <InputOTPGroup>
                    <InputOTPSlot index={0} className="size-12" />
                    <InputOTPSlot index={1} className="size-12" />
                    <InputOTPSlot index={2} className="size-12" />
                  </InputOTPGroup>
                  <InputOTPSeparator />
                  <InputOTPGroup>
                    <InputOTPSlot index={3} className="size-12" />
                    <InputOTPSlot index={4} className="size-12" />
                    <InputOTPSlot index={5} className="size-12" />
                  </InputOTPGroup>
                </InputOTP>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full">
          {submitButtonText ?? t('auth.verify')}
        </Button>

        <Button
          type="button"
          variant="ghost"
          disabled={countdown > 0}
          onClick={onResend}
        >
          {countdown > 0
            ? t('auth.resend_code_countdown', { seconds: countdown })
            : t('auth.resend_code')}
        </Button>
      </form>
    </Form>
  )
}
