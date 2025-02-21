'use client'
import { signupApi } from '@/apis'
import Toast from '@/components/Toast'
import { passwordValidation } from '@/utils/validate_rules'
import { zodResolver } from '@hookform/resolvers/zod'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import FormControl from '@mui/material/FormControl'
import FormLabel from '@mui/material/FormLabel'
import TextField from '@mui/material/TextField'
import { Controller, useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import * as z from 'zod'

const signUpSchema = z.object({
  name: z.string().nonempty(),
  email: z.string().email(),
  password: passwordValidation,
})
type SignUpFormInputs = z.infer<typeof signUpSchema>

interface SignUpFormProps {
  onSuccess: (token: string, email: string) => void
}

export default function SignUpForm({ onSuccess }: SignUpFormProps) {
  const { t } = useTranslation(['auth', 'global'])

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<SignUpFormInputs>({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
    },
    mode: 'onChange'
  })

  const onSubmit = async (data: SignUpFormInputs) => {
    try {
      const res = await signupApi(data)
      if (res.data?.token) {
        Toast.success({ message: t('signup_success') })
        onSuccess(res.data.token, data.email)
      }
    }
    catch (e) {
      console.error(e)
      Toast.error({ message: t('signup_failed') })
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      sx={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 2 }}
    >
      <FormControl>
        <FormLabel htmlFor="name">{t('full_name')}</FormLabel>
        <Controller
          name="name"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              id="name"
              placeholder={t('full_name')}
              fullWidth
              variant="outlined"
              error={!!errors.name}
              helperText={errors.name ? t('name_required') : undefined}
            />
          )}
        />
      </FormControl>
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
              helperText={errors.email ? t('enter_valid_email') : undefined}
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
              autoComplete="new-password"
              fullWidth
              variant="outlined"
              error={!!errors.password}
              helperText={errors.password ? t(errors.password.message as string) : undefined}
            />
          )}
        />
      </FormControl>
      <Button type="submit" fullWidth variant="contained">
        {t('sign_up', {
          ns: 'global',
        })}
      </Button>
    </Box>
  )
}
