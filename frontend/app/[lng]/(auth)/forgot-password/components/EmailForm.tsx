'use client'

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
import { useTranslation } from '@/plugins/i18n/client'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'

const emailSchema = z.object({
  email: z.string().email('auth.text.enter_valid_email'),
})

type EmailFormInputs = z.infer<typeof emailSchema>

interface EmailFormProps {
  onSubmit: (data: EmailFormInputs) => Promise<void>
  initialEmail?: string
}

export default function EmailForm({ onSubmit, initialEmail = '' }: EmailFormProps) {
  const { t } = useTranslation(['auth'])

  const form = useForm<EmailFormInputs>({
    resolver: zodResolver(emailSchema),
    defaultValues: { email: initialEmail },
    mode: 'onChange',
  })

  return (
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

        <Button type="submit" className="w-full">
          {t('auth.text.send_code')}
        </Button>
      </form>
    </Form>
  )
}
