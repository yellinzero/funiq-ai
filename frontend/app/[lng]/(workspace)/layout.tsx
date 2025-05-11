import { meOptions } from '@/apis'
import { getQueryClient } from '@/utils/get-query-client'
import { WorkspaceProvider } from './components/WorkspaceProvider'
import { WorkspaceSidebarLayout } from './components/WorkspaceSidebarLayout'


export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient()

  void queryClient.prefetchQuery(meOptions)
  return (
    <WorkspaceProvider>
      <WorkspaceSidebarLayout>
        {children}
      </WorkspaceSidebarLayout>
    </WorkspaceProvider>
  )
}
