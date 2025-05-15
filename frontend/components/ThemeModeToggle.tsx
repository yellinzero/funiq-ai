'use client'

import { Button } from '@/components/base/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/base/dropdown-menu'
import { useTranslation } from '@/plugins/i18n/client'
import { Monitor, Moon, Sun } from 'lucide-react'

import { useTheme } from 'next-themes'
import * as React from 'react'

export default function ThemeModeToggle() {
  const { t } = useTranslation(['global'])
  const { setTheme } = useTheme()

  const handleMode = (targetMode: 'system' | 'light' | 'dark') => {
    setTheme(targetMode)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="size-9 text-muted-foreground">
          <Sun className="size-4.5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute size-4.5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">{t('global.toggle_theme')}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleMode('system')}>
          <Monitor className="mr-2 h-4 w-4" />
          <span>{t('global.system')}</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleMode('light')}>
          <Sun className="mr-2 h-4 w-4" />
          <span>{t('global.light')}</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleMode('dark')}>
          <Moon className="mr-2 h-4 w-4" />
          <span>{t('global.dark')}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
