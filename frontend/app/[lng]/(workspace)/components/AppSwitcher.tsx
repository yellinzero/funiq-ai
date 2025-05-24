'use client'

import AppNameBox from '@/app/[lng]/(workspace)/apps/components/AppNameBox'
import { useAppStore } from '@/app/[lng]/(workspace)/apps/stores/use-app-store'
import { useAppsQuery, useAppsStore, useCreateAppMutation } from '@/app/[lng]/(workspace)/apps/stores/use-apps-store'
import { Button } from '@/components/base/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/base/dropdown-menu'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import { ChevronDown, Plus } from 'lucide-react'
import { usePathname, useRouter } from 'next/navigation'
import { useState } from 'react'
import { toast } from 'sonner'
import { AppEditDialog } from '../apps/components/AppEditDialog'

export default function AppSwitcher() {
  useAppsQuery()
  const { t } = useTranslation(['app', 'global'])
  const pathname = usePathname()
  const router = useRouter()
  const { app } = useAppStore()
  const { apps } = useAppsStore()
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const createApp = useCreateAppMutation()

  if (!pathname.includes('/apps/') || !app)
    return null

  return (
    <>
      <DropdownMenu open={isDropdownOpen} onOpenChange={setIsDropdownOpen}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-9 gap-2">
            <AppNameBox
              info={app}
              avatarClassName="size-6 rounded-md"
              wrapperClassName="flex items-center gap-2"
            >
              <span className="text-sm font-medium">{app.name}</span>
            </AppNameBox>
            <ChevronDown className="size-4 text-muted-foreground" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="center" className="w-[280px]">
          {apps.map(item => (
            <DropdownMenuItem
              key={item.id}
              className={cn('flex items-center gap-2 py-2 cursor-pointer', item.id === app.id && 'bg-accent')}
              onClick={() => router.push(`/apps/${item.id}`)}
            >
              <AppNameBox
                info={item}
                avatarClassName="size-6 rounded-md"
                wrapperClassName="flex items-center gap-2"
              >
                <span className="text-sm font-medium">{item.name}</span>
              </AppNameBox>
            </DropdownMenuItem>
          ))}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            className="flex items-center gap-2 py-2"
            onClick={() => {
              setIsDropdownOpen(false)
              setIsDialogOpen(true)
            }}
          >
            <Plus className="size-4" />
            <span className="text-sm">{t('app.create_app')}</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <AppEditDialog
        isOpen={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        mode="create"
        onSubmit={async (data) => {
          await createApp.mutateAsync(data)
          toast.success(t('global.text.create_successfully'))
        }}
      />
    </>
  )
}
