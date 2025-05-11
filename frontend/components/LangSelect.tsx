'use client'

import { languagesOptions } from '@/plugins/i18n/settings'
import * as React from 'react'
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

import { useChangeLanguage } from '@/plugins/i18n/client'
export default function LangSelect() {
  const { i18n } = useTranslation()
  const { changeLanguage } = useChangeLanguage()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="size-9 text-muted-foreground"
        >
          <Languages className="size-4.5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {languagesOptions.map(option => (
          <DropdownMenuItem
            key={option.value}
            className={cn(
              'cursor-pointer',
              i18n.resolvedLanguage === option.value && 'bg-accent'
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
