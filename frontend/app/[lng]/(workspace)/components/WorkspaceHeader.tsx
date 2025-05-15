'use client'

import { SidebarTrigger } from '@/components/base/sidebar'
import ThemeModeToggle from '@/components/ThemeModeToggle'
import { useWorkspaceHeader } from './WorkspaceHeaderProvider'

export default function WorkspaceHeader() {
  const { headerContent } = useWorkspaceHeader()
  const { leftContent, centerContent, rightContent } = headerContent

  return (
    <header className="flex py-1 shrink-0 items-center gap-2 transition-[width,height] ease-linear">
      <div className="flex items-center gap-2 px-4 justify-between w-full">
        <div className="flex items-center gap-2">
          <SidebarTrigger className="-ml-1 size-9 text-muted-foreground" />
          {leftContent}
        </div>

        <div className="flex-1 flex items-center justify-center">
          {centerContent}
        </div>

        <div className="flex items-center gap-2">
          {rightContent}
          <ThemeModeToggle />
        </div>
      </div>
    </header>
  )
}
