'use client'

import type { BaseWorkflowNodeProps } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/base/tooltip'
import { TruncatedText } from '@/components/TruncatedText'
import { cn } from '@/utils/ui'
import { Handle, Position } from '@xyflow/react'
import { useMemo } from 'react'
import { useAwareness } from '../AwarenessProvider'

export default function BaseNode({ data, icon, id }: BaseWorkflowNodeProps & {
  icon?: React.ReactNode
}) {
  const needTarget = data.operator !== 'start'
  const needSource = data.operator !== 'end'
  const { onlineUsers, currentClientId } = useAwareness()

  const selectingUsers = useMemo(() => {
    return Array.from(onlineUsers.entries())
      .filter(([clientId, user]) =>
        clientId !== currentClientId
        && user.selectedNodes?.includes(id),
      )
      .map(([_, user]) => user)
  }, [onlineUsers, currentClientId, id])

  const firstSelectingUser = selectingUsers[0]
  const otherSelectingUsers = selectingUsers.slice(1)
  const userBoxText = useMemo(() => {
    if (firstSelectingUser) {
      let text = firstSelectingUser.name
      if (otherSelectingUsers.length > 0) {
        text += ` + ${otherSelectingUsers.length}`
      }
      return text
    }

    return ''
  }, [firstSelectingUser, otherSelectingUsers])

  return (
    <div className="relative">
      <div
        className={cn(
          'px-4 py-2 shadow-lg rounded bg-card border',
        )}
        style={{
          borderColor: firstSelectingUser?.color,
        }}
      >
        {needTarget && <Handle type="target" position={Position.Left} />}

        <div className="flex gap-2 items-center">
          {icon}
          <div className="font-medium">{data.name}</div>
        </div>

        {needSource && <Handle type="source" position={Position.Right} />}
      </div>

      {firstSelectingUser && (
        <div className="absolute -bottom-5 right-0">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div
                  className="w-10 h-5 leading-4 px-1 rounded overflow-hidden flex items-center justify-center"
                  style={{ backgroundColor: firstSelectingUser.color }}
                >
                  <TruncatedText disabled={selectingUsers.length > 1} className="text-xs text-white" text={userBoxText} />
                </div>
              </TooltipTrigger>
              {selectingUsers.length > 1 && (
                <TooltipContent>
                  <p className="text-xs">
                    {selectingUsers.map(user => user.name).join(', ')}
                  </p>
                </TooltipContent>
              )}
            </Tooltip>
          </TooltipProvider>
        </div>
      )}
    </div>
  )
}
