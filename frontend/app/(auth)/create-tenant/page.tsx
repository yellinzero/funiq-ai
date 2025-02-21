'use client'
import { createTenantApi, tenantsOptions } from '@/apis'
import Toast from '@/components/Toast'
import { zodResolver } from '@hookform/resolvers/zod'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import MuiCard from '@mui/material/Card'
import FormControl from '@mui/material/FormControl'
import FormLabel from '@mui/material/FormLabel'
import { styled } from '@mui/material/styles'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useSuspenseQuery } from '@tanstack/react-query'
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

const tenantSchema = z.object({
  name: z.string().min(1, 'Tenant name is required'),
})

type TenantFormInputs = z.infer<typeof tenantSchema>

export default function CreateTenant() {
  const { t } = useTranslation(['auth', 'global'])
  const router = useRouter()
  const { refetch } = useSuspenseQuery(tenantsOptions)

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<TenantFormInputs>({
    resolver: zodResolver(tenantSchema),
    defaultValues: { name: '' },
    mode: 'onChange'
  })

  const onSubmit = async (data: TenantFormInputs) => {
    try {
      await createTenantApi(data)
      await refetch()
      Toast.success({ message: t('tenant_created_success') })
      router.push('/chat')
    }
    catch (e) {
      console.error('Create tenant error:', e)
      Toast.error({ message: t('tenant_creation_failed') })
    }
  }

  return (
    <Card>
      <Typography
        component="h1"
        variant="h4"
        sx={{ width: '100%', fontSize: '1.5rem' }}
      >
        {t('create_tenant')}
      </Typography>
      <Typography variant="body1" color="text.secondary">
        {t('create_tenant_description')}
      </Typography>

      <Box
        component="form"
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        sx={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 2 }}
      >
        <FormControl>
          <FormLabel htmlFor="name">{t('tenant_name')}</FormLabel>
          <Controller
            name="name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                id="name"
                placeholder={t('enter_tenant_name')}
                fullWidth
                variant="outlined"
                error={!!errors.name}
                helperText={errors.name ? t('tenant_name_required') : undefined}
              />
            )}
          />
        </FormControl>
        <Button type="submit" fullWidth variant="contained">
          {t('create_tenant')}
        </Button>
      </Box>
    </Card>
  )
}
