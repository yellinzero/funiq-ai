'use client'

import { I18N_COOKIE_NAME, languagesOptions } from '@/plugins/i18n/settings'
import { useRouter } from 'next/navigation'
import * as React from 'react'
import { useCookies } from 'react-cookie'
import { useTranslation } from 'react-i18next'
import { Languages } from 'lucide-react'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/base/dropdown-menu'
import { Button } from '@/components/base/button'
import { cn } from '@/utils/ui'

export default function LangSelect() {
  const router = useRouter()
  const [_cookie, setCookie] = useCookies()
  const { i18n } = useTranslation()
  const currLangLabel = languagesOptions.find(option => option.value === i18n.language)?.label || 'English'

  function changeLanguage(lang: string) {
    i18n.changeLanguage(lang)
    setCookie(I18N_COOKIE_NAME, lang, { path: '/' })
    router.refresh()
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex items-center gap-2 text-muted-foreground"
        >
          <Languages className="h-4 w-4" />
          <span>{currLangLabel}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {languagesOptions.map(option => (
          <DropdownMenuItem
            key={option.value}
            className={cn(
              'cursor-pointer',
            )}
            onClick={() => changeLanguage(option.value)}
          >
            {option.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
