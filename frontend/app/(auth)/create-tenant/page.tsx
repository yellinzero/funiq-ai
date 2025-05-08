'use client'

import { createTenantApi, tenantsOptions } from '@/apis'
import { toast } from 'sonner'
import { zodResolver } from '@hookform/resolvers/zod'
import { useSuspenseQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import * as z from 'zod'
import { Card, CardContent } from '@/components/base/card'
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
import { useSessionCookie } from '@/hooks/useSessionCookie'

const tenantSchema = z.object({
  name: z.string().min(1, 'auth.tenant_name_required'),
})

type TenantFormInputs = z.infer<typeof tenantSchema>

export default function CreateTenant() {
  const { t } = useTranslation(['auth'])
  const router = useRouter()
  const { updateTenantId } = useSessionCookie()
  const { refetch } = useSuspenseQuery(tenantsOptions)

  const form = useForm<TenantFormInputs>({
    resolver: zodResolver(tenantSchema),
    defaultValues: { name: '' },
    mode: 'onChange'
  })

  const onSubmit = async (data: TenantFormInputs) => {
    try {
      const res = await createTenantApi(data)
      await refetch()
      toast.success(t('auth.tenant_created_success'))
      if (res.data) {
        updateTenantId(res.data.id)
        router.push('/chat')
      }

    }
    catch (e) {
      console.error('Create tenant error:', e)
      toast.error(t('auth.tenant_creation_failed'))
    }
  }

  return (
    <Card className="w-full max-w-[450px] mx-auto p-6 space-y-4">
      <CardContent className="p-0 space-y-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          {t('auth.create_tenant')}
        </h1>

        <p className="text-muted-foreground">
          {t('auth.create_tenant_description')}
        </p>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t('auth.tenant_name')}</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder={t('auth.enter_tenant_name')}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full">
              {t('auth.create_tenant')}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
