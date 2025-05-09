'use client'

import { MessageSquare, AppWindow, Store, Wrench } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useRouter, usePathname } from 'next/navigation'
import {
  SidebarContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/base/sidebar"
import { cn } from '@/utils/ui'

export default function WorkspaceSidebarContent() {
  const { t } = useTranslation()
  const router = useRouter()
  const pathname = usePathname()

  const isSelected = (path: string) => {
    return pathname?.startsWith(path) ?? false
  }

  const menuItems = [
    {
      title: t('global.chats'),
      url: '/chat',
      icon: MessageSquare,
      isActive: isSelected('/chat')
    },
    {
      title: t('global.apps'),
      url: '/workflows',
      icon: AppWindow,
      isActive: isSelected('/apps')
    },
    // {
    //   title: t('global.store'),
    //   url: '/store',
    //   icon: Store,
    //   isActive: isSelected('/store')
    // },
    {
      title: t('global.toolkit'),
      url: '/toolkit',
      icon: Wrench,
      isActive: isSelected('/toolkit')
    }
  ]

  return (
    <SidebarContent>
      <SidebarMenu>
        {menuItems.map((item) => (
          <SidebarMenuItem key={item.title}>
            <SidebarMenuButton
              tooltip={item.title}
              onClick={() => router.push(item.url)}
              className={cn(
                isSelected(item.url) ? "bg-accent text-accent-foreground" : "",
                "cursor-pointer"
              )}
            >
              <item.icon className="h-4 w-4" />
              <span>{item.title}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarContent>

  )
}
