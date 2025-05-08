'use client'
import type { IAccountResponse } from '@/apis/types'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/base/avatar'

interface IUserInfoBoxProps {
  userInfo?: IAccountResponse
  showName?: boolean
  showEmail?: boolean
}

export default function CurrentUserInfoBox({
  userInfo,
  showName = false,
  showEmail = false,
}: IUserInfoBoxProps) {
  if (!userInfo) return null

  return (
    <div className="flex items-center justify-center gap-4">
      <Avatar className="h-9 w-9">
        <AvatarImage
          src={userInfo.avatar ?? ''}
          alt={userInfo.name ?? ''}
        />
        <AvatarFallback>
          {userInfo.name?.[0]?.toUpperCase() ?? 'U'}
        </AvatarFallback>
      </Avatar>

      {(showName || showEmail) && (
        <div className="flex flex-col gap-1">
          {showName && (
            <p className="text-sm font-medium leading-none">
              {userInfo.name}
            </p>
          )}
          {showEmail && (
            <p className="text-xs text-muted-foreground">
              {userInfo.email}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
