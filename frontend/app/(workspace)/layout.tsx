import { meOptions } from '@/apis'
import WorkspaceSideBar from '@/app/(workspace)/components/side-bar/WorkspaceSidebar'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/base/breadcrumb'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/base/sidebar'
import { getQueryClient } from '@/utils/get-query-client'
import { Separator } from '@radix-ui/react-separator'
import WorkspaceMainPage from './components/WorkspaceMainPage'

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient()

  void queryClient.prefetchQuery(meOptions)

  return (
    <SidebarProvider>
     <WorkspaceSideBar variant="inset"/>
      <WorkspaceMainPage>
        {children}
      </WorkspaceMainPage>
    </SidebarProvider>
  )
}
