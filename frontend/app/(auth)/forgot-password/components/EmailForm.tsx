import { zodResolver } from '@hookform/resolvers/zod'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import FormControl from '@mui/material/FormControl'
import FormLabel from '@mui/material/FormLabel'
import TextField from '@mui/material/TextField'
import { Controller, useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import * as z from 'zod'

const emailSchema = z.object({
  email: z.string().email(),
})

type EmailFormInputs = z.infer<typeof emailSchema>

interface EmailFormProps {
  onSubmit: (data: EmailFormInputs) => Promise<void>
  initialEmail?: string
}

export default function EmailForm({ onSubmit, initialEmail = '' }: EmailFormProps) {
  const { t } = useTranslation(['auth'])
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<EmailFormInputs>({
    resolver: zodResolver(emailSchema),
    defaultValues: { email: initialEmail },
    mode: 'onChange'
  })

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 2 }}>
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

      <Button type="submit" fullWidth variant="contained">
        {t('send_code')}
      </Button>
    </Box>
  )
}
