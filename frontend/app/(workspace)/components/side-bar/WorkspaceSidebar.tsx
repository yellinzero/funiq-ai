'use client'

import SideMenuContent from './WorkspaceSidebarContent'
import WorkspaceSidebarHeader from './WorkspaceSidebarHeader'
import { Sidebar } from '@/components/base/sidebar'
import WorkspaceSidebarFooter from './WorkspaceSidebarFooter'

export default function WorkspaceSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <WorkspaceSidebarHeader />
      <SideMenuContent />
      <WorkspaceSidebarFooter />
    </Sidebar>
  )
}
