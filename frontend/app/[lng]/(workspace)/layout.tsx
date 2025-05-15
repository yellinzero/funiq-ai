import { WorkspaceProvider } from './components/WorkspaceProvider'
import { WorkspaceSidebarLayout } from './components/WorkspaceSidebarLayout'

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <WorkspaceProvider>
      <WorkspaceSidebarLayout>
        {children}
      </WorkspaceSidebarLayout>
    </WorkspaceProvider>
  )
}
