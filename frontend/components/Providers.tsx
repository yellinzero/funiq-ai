'use client'
import { getQueryClient } from '@/utils/get-query-client'

import { AppProgressProvider as ProgressProvider } from '@bprogress/next'
import { QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from 'next-themes'
import { CookiesProvider } from 'react-cookie'

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
