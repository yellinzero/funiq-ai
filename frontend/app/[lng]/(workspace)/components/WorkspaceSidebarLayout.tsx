'use client'
import WorkspaceSideBar from '@/app/[lng]/(workspace)/components/side-bar/WorkspaceSidebar'
import { SidebarProvider } from '@/components/base/sidebar'
import WorkspaceMainPage from './WorkspaceMainPage'
import { useWorkspace } from './WorkspaceProvider'

export function WorkspaceSidebarLayout({ children }: { children: React.ReactNode }) {
  const { isInApp } = useWorkspace()
  return (
    <SidebarProvider style={
      {
        '--sidebar-width': isInApp ? '13rem' : '10rem',
      } as React.CSSProperties
    }
    >
      <WorkspaceSideBar variant="inset" />
      <WorkspaceMainPage>
        {children}
      </WorkspaceMainPage>
    </SidebarProvider>
  )
}
