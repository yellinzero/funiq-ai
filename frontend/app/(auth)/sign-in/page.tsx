'use client'

import { loginApi } from '@/apis'
import { HttpError } from '@/apis/core'
import { toast } from 'sonner'
import { useSessionCookie } from '@/hooks/useSessionCookie'
import { zodResolver } from '@hookform/resolvers/zod'
import { passwordValidation } from '@/utils/constants'
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
import Link from 'next/link'

const loginSchema = z.object({
  email: z.string().email('auth.enter_valid_email'),
  password: passwordValidation,
})
type LoginFormInputs = z.infer<typeof loginSchema>

export default function Login() {
  const { t } = useTranslation(['auth', 'global'])
  const { setAuth } = useSessionCookie()
  const router = useRouter()

  const form = useForm<LoginFormInputs>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
    mode: 'onChange'
  })

  const emailValue = form.watch('email')

  const onSubmit = async (data: LoginFormInputs) => {
    try {
      const res = await loginApi(data)
      if (res.data) {
        setAuth(res.data.access_token, res.data.tenant_id ?? undefined)
        router.push('/chat')
        toast.success(t('auth.login_success'))
      }
    }
    catch (e: unknown) {
      console.error('Login error:', e)
      if (e instanceof HttpError && e.code === 'B0102') {
        router.push(`/activate?email=${encodeURIComponent(data.email)}`)
      }
    }
  }

  return (
    <div className="flex flex-col items-center gap-4 w-full max-w-[450px] h-[70%]">
      <Card className="flex-1 p-6 w-full shadow-lg">
        <CardContent className="p-0 space-y-4">
          <h1 className="text-2xl font-semibold tracking-tight">
            {t('global.welcome', {
              name: t('global.product_name'),
            })}
          </h1>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('auth.email')}</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="email"
                        placeholder="your@email.com"
                        autoComplete="email"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('auth.password')}</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="password"
                        placeholder="••••••"
                        autoComplete="current-password"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full">
                {t('global.sign_in')}
              </Button>

              <div className="flex justify-end">
                <Link
                  href={`/forgot-password${emailValue ? `?email=${encodeURIComponent(emailValue)}` : ''}`}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {t('auth.forgot_password')}
                </Link>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>

      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">
          {t('auth.no_account')}
        </span>
        <Link
          href="/sign-up"
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          {t('auth.sign_up_now')}
        </Link>
      </div>
    </div>
  )
}
