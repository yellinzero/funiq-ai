'use client'

import {
  SidebarMenu,
  SidebarMenuItem,
  useSidebar,
} from '@/components/base/sidebar'
import { Logo, LogoWithName } from '@/components/SiteLogo'
import { cn } from '@/utils/ui'

export default function WorkspaceSidebarHeader() {
  const { state } = useSidebar()

  const isCollapsed = state === 'collapsed'
  return (
    <SidebarMenu>
      <SidebarMenuItem className="h-10 flex items-center mb-4 shrink-0 overflow-hidden">
        <div className={cn(isCollapsed ? 'block' : 'hidden', 'shrink-0')}>
          <Logo height={32} width={32} />
        </div>
        <div className={cn(isCollapsed ? 'hidden' : 'block', 'shrink-0')}>
          <LogoWithName height={32} width={110} />
        </div>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
