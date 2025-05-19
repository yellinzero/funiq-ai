'use client'
import type { Locale } from '@/plugins/i18n/settings'
import { getQueryClient } from '@/utils/get-query-client'
import { setDayJsLang } from '@/utils/time'

import { AppProgressProvider as ProgressProvider } from '@bprogress/next'
import { QueryClientProvider } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { ThemeProvider } from 'next-themes'
import { CookiesProvider } from 'react-cookie'
import { MessageBoxProvider } from './MessageBox'

interface ProvidersProps {
  children: React.ReactNode
}

export default function Providers({ children }: ProvidersProps) {
  const queryClient = getQueryClient()
  const { lng } = useParams()
  setDayJsLang(lng as Locale)
  return (
    <ProgressProvider options={{ showSpinner: false }}>
      <CookiesProvider>
        <ThemeProvider attribute="class" enableSystem>
          <QueryClientProvider client={queryClient}>
            <MessageBoxProvider>
              {children}
            </MessageBoxProvider>
          </QueryClientProvider>
        </ThemeProvider>
      </CookiesProvider>
    </ProgressProvider>
  )
}
