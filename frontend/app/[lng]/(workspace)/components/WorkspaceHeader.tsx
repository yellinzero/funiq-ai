'use client'

import AppSwitcher from '@/app/[lng]/(workspace)/components/AppSwitcher'
import { SidebarTrigger } from '@/components/base/sidebar'
import ThemeModeToggle from '@/components/ThemeModeToggle'

export default function WorkspaceHeader() {
  return (
    <header className="flex py-1 shrink-0 items-center gap-2 transition-[width,height] ease-linear">
      <div className="flex items-center gap-2 px-4 justify-between w-full">
        <div className="flex items-center gap-2">
          <SidebarTrigger className="-ml-1 size-9 text-muted-foreground" />
        </div>

        <div className="flex-1 flex items-center justify-center">
          <AppSwitcher />
        </div>

        <div className="flex items-center gap-2">
          <ThemeModeToggle />
        </div>
      </div>
    </header>
  )
}
