'use client'
import type { Locale } from '@/plugins/i18n/settings'
import I18nProvider from '@/components/I18nProvider'
import { getQueryClient } from '@/utils/get-query-client'

import { ThemeProvider } from "next-themes"
import { QueryClientProvider } from '@tanstack/react-query'
import { CookiesProvider, useCookies } from 'react-cookie'
import { THEME_COOKIE_NAME } from '@/utils/constants'

interface ProvidersProps {
  children: React.ReactNode
  locale: Locale
}

export default function Providers({ children, locale }: ProvidersProps) {
  const [cookies, setCookie] = useCookies()
  let themeCookie = cookies[THEME_COOKIE_NAME]
  if (!themeCookie) {
    themeCookie = 'system'
    setCookie(THEME_COOKIE_NAME, themeCookie)
  }
  const queryClient = getQueryClient()
  return (
    <CookiesProvider>
      <ThemeProvider attribute="class" defaultTheme={themeCookie} enableSystem disableTransitionOnChange>
        <QueryClientProvider client={queryClient}>
          <I18nProvider locale={locale}>
            {children}
          </I18nProvider>
        </QueryClientProvider>
      </ThemeProvider>
    </CookiesProvider>
  )
}
