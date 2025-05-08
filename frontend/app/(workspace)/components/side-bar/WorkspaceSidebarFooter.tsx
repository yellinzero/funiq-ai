'use client'

import {
  Languages,
  User,
  Settings,
  LogOut,
  ChevronsUpDown,
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useCookies } from 'react-cookie'
import { useTranslation } from 'react-i18next'
import { useSuspenseQuery } from '@tanstack/react-query'
import { meOptions } from '@/apis'
import { logoutApi } from '@/apis/openapis/auth'
import { useSessionCookie } from '@/hooks/useSessionCookie'
import { I18N_COOKIE_NAME, languagesOptions } from '@/plugins/i18n/settings'
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/base/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/base/dropdown-menu'
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/base/sidebar"
import { cn } from '@/utils/ui'

export default function WorkspaceSidebarFooter() {
  const { data } = useSuspenseQuery(meOptions)
  const userInfo = data?.data
  const { t, i18n } = useTranslation()
  const [_cookie, setCookie] = useCookies()
  const sessionCookie = useSessionCookie()
  const router = useRouter()
  const { isMobile } = useSidebar()

  const handleChangeLang = (lang: string) => {
    i18n.changeLanguage(lang)
    setCookie(I18N_COOKIE_NAME, lang, { path: '/' })
    router.refresh()
  }

  async function handleLogout() {
    await logoutApi()
    sessionCookie.clearAuth()
    router.push('/')
  }

  if (!userInfo) return null

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <Avatar className="h-8 w-8 rounded-lg">
                <AvatarImage src={userInfo.avatar ?? ''} alt={userInfo.name ?? ''} />
                <AvatarFallback className="rounded-lg">
                  {userInfo.name?.[0]?.toUpperCase() ?? 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">{userInfo.name}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-lg">
                  <AvatarImage src={userInfo.avatar ?? ''} alt={userInfo.name ?? ''} />
                  <AvatarFallback className="rounded-lg">
                    {userInfo.name?.[0]?.toUpperCase() ?? 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">{userInfo.name}</span>
                  <span className="truncate text-xs">{userInfo.email}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuGroup>
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>
                  <Languages className="mr-2 size-4 text-muted-foreground" />
                  <span>{t('global.language')}</span>
                </DropdownMenuSubTrigger>
                <DropdownMenuSubContent>
                  {languagesOptions.map(item => (
                    <DropdownMenuItem
                      key={item.value}
                      onClick={() => handleChangeLang(item.value)}
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
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="size-4" />
              {t('global.logout')}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
