'use client'
import { getQueryClient } from '@/utils/get-query-client'

import { ThemeProvider } from "next-themes"
import { QueryClientProvider } from '@tanstack/react-query'
import { CookiesProvider, useCookies } from 'react-cookie'
import { AppProgressProvider as ProgressProvider } from '@bprogress/next';
interface ProvidersProps {
  children: React.ReactNode
}

export default function Providers({ children }: ProvidersProps) {
  const queryClient = getQueryClient()
  return (
    <ProgressProvider options={{ showSpinner: false }}>
      <CookiesProvider>
        <ThemeProvider attribute="class" enableSystem>
          <QueryClientProvider client={queryClient}>
              {children}
          </QueryClientProvider>
        </ThemeProvider>
      </CookiesProvider>
    </ProgressProvider>
  )
}
