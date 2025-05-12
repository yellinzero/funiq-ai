'use client'

import { logoutApi } from '@/apis/openapis/auth'
import { useSessionCookie } from '@/hooks/use-session-cookie'
import { languagesOptions } from '@/plugins/i18n/settings'
import { LogOut, Languages } from 'lucide-react'
import { useRouter } from 'next/navigation'
import * as React from 'react'
import { useTranslation } from 'react-i18next'
import CurrentUserInfoBox from '@/components/CurrentUserInfoBox'
import { useSuspenseQuery } from '@tanstack/react-query'
import { meOptions } from '@/apis'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/base/dropdown-menu'
import { cn } from '@/utils/ui'
import { useChangeLanguage } from '@/plugins/i18n/client'

export default function UserActionsMenu() {
  const { data } = useSuspenseQuery(meOptions)
  const userInfo = data?.data
  const { t, i18n } = useTranslation()
  const sessionCookie = useSessionCookie()
  const router = useRouter()
  const { changeLanguage } = useChangeLanguage()

  async function handleLogout() {
    await logoutApi()
    sessionCookie.clearAuth()
    router.push('/')
  }

  return (
    <>
      <div className="flex w-full items-center justify-center gap-4 border-t p-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <div className="cursor-pointer">
              <CurrentUserInfoBox userInfo={userInfo} />
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem>
              {t('global.my_account')}
            </DropdownMenuItem>
            <DropdownMenuItem>
              {t('global.settings')}
            </DropdownMenuItem>

            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <Languages className="mr-2 h-4 w-4" />
                <span>{t('global.language')}</span>
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                {languagesOptions.map(item => (
                  <DropdownMenuItem
                    key={item.value}
                    onClick={() => changeLanguage(item.value)}
                    className={cn(
                      'cursor-pointer',
                      i18n.language === item.value && 'bg-accent'
                    )}
                  >
                    {item.label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>

            <DropdownMenuSeparator />

            <DropdownMenuItem onClick={handleLogout}>
              <span className="flex-1">{t('global.logout')}</span>
              <LogOut className="h-4 w-4" />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </>
  )
}
