import { initTranslations } from '@/plugins/i18n'
import { getLocaleFromServer } from '@/plugins/i18n/server'

import { Roboto } from 'next/font/google'
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript'
import React from 'react'
import Providers from '@/components/Providers'

const namespaces = ['global']

export const roboto = Roboto({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto',
  preload: false,
})

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const locale = await getLocaleFromServer()
  await initTranslations(locale, namespaces)
  return (
    <React.StrictMode>
      <html lang={locale} className={roboto.variable} suppressHydrationWarning>
        <body style={
          {
            width: '100vw',
            height: '100vh',
          }
        }
        >
          <InitColorSchemeScript />
          <Providers locale={locale}>
            {children}
          </Providers>
        </body>
      </html>
    </React.StrictMode>

  )
}
