import { Button } from '@/components/base/button'
import ThemeModeToggle from '@/components/ThemeModeToggle'
import { SidebarTrigger } from '@/components/base/sidebar'

export default function WorkspaceHeader() {
  return (
    <header className="flex py-1 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
      <div className="flex items-center gap-2 px-4 justify-between w-full">
        <SidebarTrigger className="-ml-1 size-9 text-muted-foreground" />
        <div className="flex items-center">
          <ThemeModeToggle />
        </div>
      </div>
    </header>
  )
}
