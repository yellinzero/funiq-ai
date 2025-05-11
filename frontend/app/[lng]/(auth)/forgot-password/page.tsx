'use client'

import { forgotPasswordApi, resendVerificationCodeApi, resetPasswordApi } from '@/apis'
import { toast } from 'sonner'
import { useCountdown } from '@/hooks/useCountdown'
import { useRouter, useSearchParams } from 'next/navigation'
import { useState } from 'react'
import { useTranslation } from '@/plugins/i18n/client'
import EmailForm from './components/EmailForm'
import ResetForm from './components/ResetForm'
import { Card, CardContent } from '@/components/base/card'

export default function ForgotPassword() {
  const { t } = useTranslation(['auth'])
  const router = useRouter()
  const searchParams = useSearchParams()
  const [step, setStep] = useState<1 | 2>(1)
  const [token, setToken] = useState('')
  const [email, setEmail] = useState(searchParams.get('email') || '')
  const { countdown, startCountdown } = useCountdown()

  const onSubmitEmail = async (data: { email: string }) => {
    try {
      setEmail(data.email)
      const res = await forgotPasswordApi({
        email: data.email,
      })
      if (res.data?.token) {
        setToken(res.data.token)
        setStep(2)
        toast.success(t('auth.reset_code_sent'))
      }
    }
    catch (e) {
      console.error('Send reset code error:', e)
    }
  }

  const onSubmitReset = async (data: { code: string, password: string, confirmPassword: string }) => {
    try {
      await resetPasswordApi({
        token,
        code: data.code,
        new_password: data.password,
      })
      toast.success(t('auth.password_reset_success'))
      router.push('/sign-in')
    }
    catch (e) {
      console.error('Reset password error:', e)
    }
  }

  return (
    <Card className="w-full max-w-[450px] mx-auto p-6 space-y-4 h-[70%]">
      <CardContent className="p-0 space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          {t('auth.forgot_password')}
        </h1>

      {step === 1
        ? <EmailForm onSubmit={onSubmitEmail} initialEmail={email} />
        : (
            <ResetForm
              onSubmit={onSubmitReset}
              countdown={countdown}
              onResend={async () => {
                await resendVerificationCodeApi({ email, code_type: 'reset_password_email' })
                startCountdown()
              }}
            />
          )}
      </CardContent>
    </Card>
  )
}
