import { initTranslations } from '@/plugins/i18n'
import { getLocaleFromServer } from '@/plugins/i18n/server'

import { Roboto } from 'next/font/google'
import React from 'react'
import Providers from '@/components/Providers'
import './globals.css'
import { Toaster } from '@/components/base/sonner'
const namespaces = ['global']

export const roboto = Roboto({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto',
  preload: true,
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
        <body className="w-full h-screen">
          <Providers locale={locale}>
            {children}
          </Providers>
          <Toaster richColors position="top-right" />
        </body>
      </html>
    </React.StrictMode>

  )
}
