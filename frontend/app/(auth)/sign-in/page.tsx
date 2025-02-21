'use client'
import { loginApi } from '@/apis'
import { HttpError } from '@/apis/core'
import Toast from '@/components/Toast'
import { useSessionCookie } from '@/hooks/useSessionCookie'
import { zodResolver } from '@hookform/resolvers/zod'
import { passwordValidation } from '@/utils/validate_rules'
import { Link } from '@mui/material'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import MuiCard from '@mui/material/Card'
import FormControl from '@mui/material/FormControl'
import FormLabel from '@mui/material/FormLabel'
import { styled } from '@mui/material/styles'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useRouter } from 'next/navigation'
import { Controller, useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import * as z from 'zod'

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

const loginSchema = z.object({
  email: z.string().email(),
  password: passwordValidation,
})
type LoginFormInputs = z.infer<typeof loginSchema>

export default function Login() {
  const { t } = useTranslation(['auth', 'global'])
  const { setAuth } = useSessionCookie()
  const router = useRouter()

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<LoginFormInputs>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
    mode: 'onChange'
  })

  const emailValue = watch('email')

  const onSubmit = async (data: LoginFormInputs) => {
    try {
      const res = await loginApi(data)
      if (res.data) {
        setAuth(res.data.access_token, res.data.tenant_id ?? undefined)

        router.push('/chat')

        Toast.success({ message: t('login_success') })
      }
    }
    catch (e: unknown) {
      console.error('Login error:', e)
      if (e instanceof HttpError && e.code === 'B0004') {
        router.push(`/activate?email=${encodeURIComponent(data.email)}`)
      }
    }
  }

  return (
    <>
      <Card sx={{ height: '70%' }}>
        <Typography
          component="h1"
          variant="h4"
          sx={{ width: '100%', fontSize: '1.5rem' }}
        >
          {t('welcome', {
            name: t('product_name', {
              ns: 'global',
            }),
            ns: 'global',
          })}
        </Typography>
        <Box
          component="form"
          onSubmit={handleSubmit(onSubmit)}
          noValidate
          sx={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 2 }}
        >
          <FormControl>
            <FormLabel htmlFor="email">{t('email')}</FormLabel>
            <Controller
              name="email"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  autoComplete="email"
                  fullWidth
                  variant="outlined"
                  error={!!errors.email}
                  helperText={errors.email
                    ? t('enter_valid_email')
                    : undefined}
                />
              )}
            />
          </FormControl>
          <FormControl>
            <FormLabel htmlFor="password">{t('password')}</FormLabel>
            <Controller
              name="password"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  id="password"
                  type="password"
                  placeholder="••••••"
                  autoComplete="current-password"
                  fullWidth
                  variant="outlined"
                  error={!!errors.password}
                  helperText={errors.password ? t(errors.password.message as string) : undefined}
                />
              )}
            />
          </FormControl>
          <Button type="submit" fullWidth variant="contained">
            {t('sign_in', {
              ns: 'global',
            })}
          </Button>
          <Box sx={{
            width: '100%',
            display: 'flex',
            justifyContent: 'end',
          }}
          >
            <Link
              href={`/forgot-password${emailValue ? `?email=${encodeURIComponent(emailValue)}` : ''}`}
              underline="hover"
            >
              {t('forgot_password')}
            </Link>
          </Box>

        </Box>
      </Card>
      <Box
        component="span"
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Box component="span" sx={{ color: 'text.secondary' }}>
          {t('no_account')}
        </Box>

        <Link href="/sign-up" underline="hover">
          {t('sign_up_now')}
        </Link>
      </Box>
    </>
  )
}
