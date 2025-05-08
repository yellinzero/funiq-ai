'use client'

import i18next from '@/plugins/i18n/client'
import React, { useState } from 'react'
import { I18nextProvider } from 'react-i18next'
import FullPageLoading from './FullPageLoading'

export default function I18nProvider({
  children,
  locale,
}: {
  children: React.ReactNode
  locale: string
}) {
  const [initialized, setInitialized] = useState(false)
  React.useEffect(() => {
    if (i18next.language !== locale) {
      i18next.changeLanguage(locale).finally(() => setInitialized(true))
    }
    else {
      setInitialized(true)
    }
  }, [locale])

  return initialized
    ? <I18nextProvider i18n={i18next}>{children}</I18nextProvider>
    : (
        <FullPageLoading />
      )
}
