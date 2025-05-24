'use client'

import { useWorkspace } from '@/app/[lng]/(workspace)/components/WorkspaceProvider'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/base/collapsible'
import {
  SidebarContent,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from '@/components/base/sidebar'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import { AppWindow, ChevronRight, MessageSquare, Wrench } from 'lucide-react'
import { usePathname } from 'next/navigation'

export default function WorkspaceSidebarContent() {
  const { t } = useTranslation(['global', 'app'])
  const pathname = usePathname()
  const { activeApp } = useWorkspace()

  const isSelected = (path: string) => {
    return pathname?.startsWith(path) ?? false
  }

  const getAppSubItems = (appId: string) => [
    {
      title: t('app.info'),
      url: `/apps/${appId}/info`,
    },
    {
      title: t('app.workflow'),
      url: `/apps/${appId}/workflow`,
    },
    {
      title: t('app.knowledge_base'),
      url: `/apps/${appId}/knowledge-base`,
    },
  ]

  const menuItems = [
    {
      title: t('global.chats'),
      url: '/chat',
      icon: MessageSquare,
      isActive: isSelected('/chat'),
    },
    {
      title: t('global.apps'),
      url: '/apps',
      icon: AppWindow,
      isActive: isSelected('/apps'),
      items: activeApp ? getAppSubItems(activeApp) : undefined,
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
      isActive: isSelected('/toolkit'),
    },
  ]

  return (
    <SidebarContent>
      <SidebarMenu>
        {menuItems.map(item => (
          <Collapsible key={item.title} asChild defaultOpen={item.isActive}>
            <SidebarMenuItem>
              <SidebarMenuButton
                asChild
                tooltip={item.title}
              >
                <a
                  href={item.url}
                  className={cn(
                    isSelected(item.url) ? 'bg-accent text-accent-foreground' : '',
                    'cursor-pointer flex items-center',
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.title}</span>
                </a>
              </SidebarMenuButton>
              {item.items?.length
                ? (
                    <>
                      <CollapsibleTrigger asChild>
                        <SidebarMenuAction className="data-[state=open]:rotate-90">
                          <ChevronRight className="h-4 w-4" />
                          <span className="sr-only">{t('global.toggle')}</span>
                        </SidebarMenuAction>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <SidebarMenuSub>
                          {item.items?.map(subItem => (
                            <SidebarMenuSubItem key={subItem.title}>
                              <SidebarMenuSubButton
                                asChild
                              >
                                <a
                                  href={subItem.url}
                                  className={cn(
                                    isSelected(subItem.url) ? 'bg-accent text-accent-foreground' : '',
                                    'cursor-pointer',
                                  )}
                                >
                                  <span>{subItem.title}</span>
                                </a>
                              </SidebarMenuSubButton>
                            </SidebarMenuSubItem>
                          ))}
                        </SidebarMenuSub>
                      </CollapsibleContent>
                    </>
                  )
                : null}
            </SidebarMenuItem>
          </Collapsible>
        ))}
      </SidebarMenu>
    </SidebarContent>
  )
}
