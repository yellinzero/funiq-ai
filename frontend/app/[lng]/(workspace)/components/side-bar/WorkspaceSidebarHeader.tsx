'use client'

import {
  SidebarMenu,
  SidebarMenuItem,
  useSidebar,
} from '@/components/base/sidebar'
import { Logo, PureLogo } from '@/components/SiteLogo'
import { useRouter } from 'next/navigation'

export default function WorkspaceSidebarHeader() {
  const { state } = useSidebar()

  const isCollapsed = state === 'collapsed'
  const LogoComponent = isCollapsed ? PureLogo : Logo
  const router = useRouter()

  return (
    <SidebarMenu>
      <SidebarMenuItem className="h-10 flex items-center mb-4 shrink-0 overflow-hidden">
        <LogoComponent className="shrink-0 cursor-pointer" onClick={() => router.push('/')} />
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
