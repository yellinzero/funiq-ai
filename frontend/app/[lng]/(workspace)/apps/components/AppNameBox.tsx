'use client'

import type { IAppInfo } from '@/apis'
import { Avatar, AvatarFallback } from '@/components/base/avatar'
import { cn } from '@/utils/ui'

export interface AppNameBoxProps {
  info: IAppInfo
  children?: React.ReactNode
  avatarClassName?: string
  wrapperClassName?: string
  textClassName?: string
}

export default function AppNameBox({
  info,
  avatarClassName,
  wrapperClassName,
  textClassName,
  children,
}: AppNameBoxProps) {
  return (
    <div className={cn('flex items-center gap-4 h-full', wrapperClassName)}>
      <Avatar className={cn('h-12 w-12 rounded-md', avatarClassName)}>
        <AvatarFallback className="rounded-md">
          {info.name?.[0]?.toUpperCase() ?? 'A'}
        </AvatarFallback>
      </Avatar>
      {
        children || (
          <span className={cn('text-lg font-medium', textClassName)}>{info.name}</span>
        )
      }
    </div>
  )
}
