'use client'
import { SidebarInset } from '@/components/base/sidebar'
import WorkspaceHeader from './WorkspaceHeader'

export default function WorkspaceMainPage({ children }: { children: React.ReactNode }) {
  return (
    <SidebarInset>
      <WorkspaceHeader />
      {children}
    </SidebarInset>
  )
}
