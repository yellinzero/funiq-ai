'use client'

import { signupApi } from '@/apis'
import { toast } from 'sonner'
import { passwordValidation } from '@/utils/constants'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import * as z from 'zod'
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

const signUpSchema = z.object({
  name: z.string().nonempty('auth.name_required'),
  email: z.string().email('auth.enter_valid_email'),
  password: passwordValidation,
})
type SignUpFormInputs = z.infer<typeof signUpSchema>

interface SignUpFormProps {
  onSuccess: (token: string, email: string) => void
}

export default function SignUpForm({ onSuccess }: SignUpFormProps) {
  const { t } = useTranslation(['auth', 'global'])

  const form = useForm<SignUpFormInputs>({
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
        toast.success(t('auth.signup_success'))
        onSuccess(res.data.token, data.email)
      }
    }
    catch (e) {
      console.error(e)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('auth.full_name')}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  placeholder={t('auth.full_name')}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

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
                  autoComplete="new-password"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full">
          {t('global.sign_up')}
        </Button>
      </form>
    </Form>
  )
}
