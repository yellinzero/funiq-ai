'use client'
import { resendVerificationCodeApi, signupVerifyApi } from '@/apis'
import { toast } from 'sonner'
import VerificationCodeForm from '@/components/VerificationCodeForm'
import { useCountdown } from '@/hooks/useCountdown'
import { useSessionCookie } from '@/hooks/useSessionCookie'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useTranslation } from '@/plugins/i18n/client'
import SignUpForm from './components/SignUpForm'
import { Card, CardContent } from '@/components/base/card'

export default function SignUp() {
  const { t } = useTranslation(['auth', 'global'])
  const { setAuth } = useSessionCookie()
  const router = useRouter()
  const [showVerifyEmail, setShowVerifyEmail] = useState(false)
  const [token, setToken] = useState('')
  const { countdown, startCountdown } = useCountdown()
  const [email, setEmail] = useState('')

  const handleSignUpSuccess = (token: string, userEmail: string) => {
    setShowVerifyEmail(true)
    setToken(token)
    setEmail(userEmail)
    startCountdown()
  }

  const handleVerifyEmailSuccess = (data: { access_token: string, tenant_id?: string }) => {
    if (data) {
      setAuth(data.access_token, data.tenant_id)
      if (!data.tenant_id) {
        router.push('/create-tenant')
      }
      else {
        router.push('/chat')
      }
    }
  }

  const handleResendCode = async () => {
    try {
      const {data} = await resendVerificationCodeApi({ email, code_type: 'signup_email' })
      if (data) {
        setToken(data.token)
        startCountdown()
      }

    }
    catch (e) {
      console.error('Resend verification code error:', e)
    }
  }

  const handleVerificationSubmit = async (code: string) => {
    const res = await signupVerifyApi({ code, token })
    if (res.data) {
      toast.success(t('auth.email_verified_success'))
      handleVerifyEmailSuccess({
        access_token: res.data.access_token,
        tenant_id: res.data.tenant_id ?? undefined,
      })
    }
  }

  return (
    <Card className="w-full max-w-[450px] mx-auto p-6 space-y-4 h-[70%]">
      <CardContent className="p-0 space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          {t('global.welcome', {
            name: t('global.product_name'),
          })}
        </h1>

        <h2 className="text-2xl font-semibold tracking-tight text-[clamp(2rem,10vw,2.15rem)]">
          {showVerifyEmail ? t('auth.verify_email') : t('global.sign_up')}
        </h2>

        {showVerifyEmail
          ? (
              <VerificationCodeForm
                onSubmit={handleVerificationSubmit}
                countdown={countdown}
                onResend={handleResendCode}
              />
            )
          : (
              <SignUpForm onSuccess={handleSignUpSuccess} />
            )}
      </CardContent>
    </Card>
  )
}
