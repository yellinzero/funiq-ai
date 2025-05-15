'use client'

import { Sidebar } from '@/components/base/sidebar'
import SideMenuContent from './WorkspaceSidebarContent'
import WorkspaceSidebarFooter from './WorkspaceSidebarFooter'
import WorkspaceSidebarHeader from './WorkspaceSidebarHeader'

export default function WorkspaceSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <WorkspaceSidebarHeader />
      <SideMenuContent />
      <WorkspaceSidebarFooter />
    </Sidebar>
  )
}
