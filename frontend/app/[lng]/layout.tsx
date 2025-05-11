import { Roboto } from 'next/font/google'
import React from 'react'
import Providers from '@/components/Providers'
import './globals.css'
import { Toaster } from '@/components/base/sonner'

export const roboto = Roboto({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto',
  preload: true,
})

export default async function RootLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode
  params: Promise<{
    lng: string
  }>
}>) {
  const lng = (await params).lng
  return (
    <React.StrictMode>
      <html lang={lng} className={roboto.variable} suppressHydrationWarning>
        <body className="w-full h-screen">
          <Providers>
            {children}
          </Providers>
          <Toaster richColors position="top-right" />
        </body>
      </html>
    </React.StrictMode>

  )
}
