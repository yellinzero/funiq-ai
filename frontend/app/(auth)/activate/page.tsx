'use client'
import { activateAccountApi, activateAccountVerifyApi, resendVerificationCodeApi } from '@/apis'
import { toast } from 'sonner'
import VerificationCodeForm from '@/components/VerificationCodeForm'
import { useCountdown } from '@/hooks/useCountdown'
import { useSessionCookie } from '@/hooks/useSessionCookie'
import { useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent } from '@/components/base/card'
import { Button } from '@/components/base/button'

export default function Activate() {
  const { t } = useTranslation(['auth', 'global'])
  const router = useRouter()
  const searchParams = useSearchParams()
  const [token, setToken] = useState('')
  const [email, setEmail] = useState('')
  const { countdown, startCountdown } = useCountdown()
  const { setAuth } = useSessionCookie()

  useEffect(() => {
    const email = searchParams.get('email')
    if (!email) {
      toast.error(t('auth.invalid_activation_link'))
      return
    }
    setEmail(email)
  }, [searchParams, router, t])

  const sendActivationEmail = async () => {
    try {
      const res = await activateAccountApi({
        email,
      })
      if (res.data?.token) {
        setToken(res.data.token)
        startCountdown()
        toast.success(t('auth.activation_code_sent'))
      }
    }
    catch (e) {
      console.error('Send activation code error:', e)
      toast.error(t('auth.send_code_failed'))
      router.push('/sign-in')
    }
  }

  const handleResendCode = async () => {
    try {
      await resendVerificationCodeApi({
        email,
        code_type: 'activate_account_email',
      })
      startCountdown()
      toast.success(t('auth.activation_code_sent'))
    }
    catch (e) {
      console.error('Resend verification code error:', e)
      toast.error(t('auth.send_code_failed'))
    }
  }

  const handleVerificationSubmit = async (code: string) => {
    const res = await activateAccountVerifyApi({ token, code })
    if (res.data) {
      setAuth(res.data.access_token, res.data.tenant_id ?? undefined)
      toast.success(t('auth.account_activated'))
      if (!res.data.tenant_id) {
        router.push('/create-tenant')
      }
      else {
        router.push('/chat')
      }
    }
  }

  return (
    <Card className="w-full max-w-[450px] mx-auto p-6 space-y-4">
      <CardContent className="p-0 space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          {t('auth.activate_account')}
        </h1>

        <p className="text-muted-foreground">
          {t('auth.activation_code_description', { email })}
        </p>

        {!token && (
          <Button
            variant="default"
            onClick={sendActivationEmail}
            className="w-full"
          >
            {t('auth.send_activation_code')}
          </Button>
        )}

        {token && (
          <VerificationCodeForm
            onSubmit={handleVerificationSubmit}
            countdown={countdown}
            onResend={handleResendCode}
            errorMessage={t('auth.activation_failed')}
          />
        )}
      </CardContent>
    </Card>
  )
}
