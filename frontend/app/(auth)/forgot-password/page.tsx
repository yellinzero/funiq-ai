'use client'
import { forgotPasswordApi, resendVerificationCodeApi, resetPasswordApi } from '@/apis'
import Toast from '@/components/Toast'
import { useCountdown } from '@/hooks/useCountdown'
import MuiCard from '@mui/material/Card'
import { styled } from '@mui/material/styles'
import Typography from '@mui/material/Typography'
import { useRouter, useSearchParams } from 'next/navigation'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import EmailForm from './components/EmailForm'
import ResetForm from './components/ResetForm'

const Card = styled(MuiCard)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignSelf: 'center',
  width: '100%',
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  [theme.breakpoints.up('sm')]: {
    maxWidth: '450px',
  },
}))

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
        Toast.success({ message: t('reset_code_sent') })
      }
    }
    catch (e) {
      console.error('Send reset code error:', e)
      Toast.error({ message: t('send_code_failed') })
    }
  }

  const onSubmitReset = async (data: { code: string, password: string, confirmPassword: string }) => {
    try {
      await resetPasswordApi({
        token,
        code: data.code,
        new_password: data.password,
      })
      Toast.success({ message: t('password_reset_success') })
      router.push('/sign-in')
    }
    catch (e) {
      console.error('Reset password error:', e)
      Toast.error({ message: t('password_reset_failed') })
    }
  }

  return (
    <Card sx={{ height: '70%' }}>
      <Typography
        component="h1"
        variant="h4"
        sx={{ width: '100%', fontSize: '1.5rem' }}
      >
        {t('forgot_password')}
      </Typography>

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
    </Card>
  )
}
