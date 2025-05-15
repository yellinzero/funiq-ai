'use client'

import type { IAppInfo } from '@/apis'
import { useDeleteAppMutation } from '@/app/[lng]/(workspace)/apps/stores/use-apps-store'
import { useUserById } from '@/app/[lng]/stores/use-global-store'
import { Avatar, AvatarFallback } from '@/components/base/avatar'
import { Button } from '@/components/base/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/base/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/base/dropdown-menu'
import { TruncatedText } from '@/components/TruncatedText'
import { useTranslation } from '@/plugins/i18n/client'
import { getRelativeTime } from '@/utils/time'
import { Clock, MoreHorizontal, Trash2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

export interface AppCardProps {
  info: IAppInfo
}

export default function AppCard({
  info,
}: AppCardProps) {
  const { t } = useTranslation(['app', 'global'])
  const deleteApp = useDeleteAppMutation()
  const user = useUserById(info.updated_by)
  const router = useRouter()

  const handleDeleteApp = async (appId: string) => {
    try {
      await deleteApp.mutateAsync(appId)
      toast.success(t('global.text.delete_successfully'))
    }
    catch (error) {
      console.error(error)
    }
  }

  const handleCardClick = (e: React.MouseEvent) => {
    if (e.target instanceof Element
      && (e.target.closest('[data-slot="dropdown-menu"]')
        || e.target.closest('[data-slot="dropdown-menu-content"]'))) {
      return
    }
    router.push(`/apps/${info.id}/workflow`)
  }

  return (
    <Card
      key={info.id}
      className="group overflow-hidden gap-3 hover:shadow-md cursor-pointer py-4"
      onClick={handleCardClick}
    >
      <CardHeader className="px-4 gap-0">
        <div className="flex items-center gap-4 h-full">
          <Avatar className="h-12 w-12 rounded-md">
            <AvatarFallback className="rounded-md">
              {info.name?.[0]?.toUpperCase() ?? 'A'}
            </AvatarFallback>
          </Avatar>
          <CardTitle>{info.name}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="flex-1 px-4">
        <TruncatedText
          className="text-muted-foreground break-all text-sm"
          text={info.description || t('app.text.no_description')}
          lines={2}
        />
      </CardContent>
      <CardFooter className="flex items-center justify-between px-4 text-muted-foreground">
        <div className="flex items-center gap-2 text-sm flex-1">
          <div className="flex items-center gap-1">
            <Avatar className="h-5 w-5">
              <AvatarFallback className="text-xs">
                {user?.name?.[0]?.toUpperCase() ?? 'U'}
              </AvatarFallback>
            </Avatar>
            <span className="text-xs">{user?.name ?? '--'}</span>
          </div>
          <span className="text-xs">•</span>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span className="text-xs">{getRelativeTime(info.updated_at)}</span>
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreHorizontal className="h-4 w-4" />
              <span className="sr-only">Open menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => handleDeleteApp(info.id)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {t('app.delete_app')}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardFooter>
    </Card>
  )
}
