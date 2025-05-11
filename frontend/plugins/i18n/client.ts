'use client'

import i18next from './i18next'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useCookies } from 'react-cookie'
import { I18N_COOKIE_NAME } from './settings'
import { useTranslation as useTranslationCore } from 'react-i18next'
import { useRouter } from 'next/navigation'

const runsOnServerSide = typeof window === 'undefined'

export function useTranslation(ns?: string | string[], options?: Parameters<typeof useTranslationCore>[1]) {
  const lng = useParams()?.lng
  if (typeof lng !== 'string') throw new Error('useTranslation is only available inside /app/[lng]')
  if (runsOnServerSide && i18next.resolvedLanguage !== lng) {
    i18next.changeLanguage(lng)
  } else {
    const [activeLng, setActiveLng] = useState(i18next.resolvedLanguage)
    useEffect(() => {
      if (activeLng === i18next.resolvedLanguage) return
      setActiveLng(i18next.resolvedLanguage)
    }, [activeLng, i18next.resolvedLanguage])
    useEffect(() => {
      if (!lng || i18next.resolvedLanguage === lng) return
      i18next.changeLanguage(lng)
    }, [lng, i18next])
  }
  return useTranslationCore(ns, options)
}

export function useChangeLanguage() {
  const [_cookie, setCookie] = useCookies()
  const router = useRouter()
  const { i18n } = useTranslation()

  function changeLanguage(lang: string) {
    i18n.changeLanguage(lang)
    setCookie(I18N_COOKIE_NAME, lang, { path: '/' })
    router.refresh()
  }

  return {
    changeLanguage,
  }
}