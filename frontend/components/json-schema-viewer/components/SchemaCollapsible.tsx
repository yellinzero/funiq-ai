'use client'

import {
  CollapsibleContent,
  Collapsible as CollapsiblePrimitive,
  CollapsibleTrigger,
} from '@/components/base/collapsible'
import { cn } from '@/utils/ui'
import { ChevronRight } from 'lucide-react'
import React, { type FC, type ReactNode } from 'react'

interface CollapsibleProps {
  /**
   * Summary or title content shown in the header
   */
  summary: ReactNode
  /**
   * Collapsible content
   */
  children: ReactNode
  /**
   * Whether the collapsible is open by default
   */
  defaultOpen?: boolean
  /**
   * Custom class name for the root element
   */
  className?: string
  /**
   * Class name for the summary/header area
   */
  summaryClassName?: string
  /**
   * Class name for the content area
   */
  contentClassName?: string
  /**
   * Whether to show the collapsible icon
   */
  showIcon?: boolean
  /**
   * Callback invoked when open state changes
   */
  onOpenChange?: (open: boolean) => void
}

export const SchemaCollapsible: FC<CollapsibleProps> = ({
  summary,
  children,
  defaultOpen = true,
  className,
  summaryClassName,
  contentClassName,
  showIcon = true,
  onOpenChange,
}) => {
  return (
    <CollapsiblePrimitive
      defaultOpen={defaultOpen}
      onOpenChange={onOpenChange}
      className={cn('collapsible', className)}
    >
      <CollapsibleTrigger
        className={cn(
          'flex cursor-pointer items-center gap-1 select-none',
          summaryClassName,
        )}
      >
        {showIcon && (
          <span className="flex-shrink-0 text-muted-foreground">
            <ChevronRight className="size-4 transition-transform [[data-state=open]>&]:rotate-90" />
          </span>
        )}
        <div className="flex-1">{summary}</div>
      </CollapsibleTrigger>

      <CollapsibleContent className={cn('collapsible-content', contentClassName)}>
        {children}
      </CollapsibleContent>
    </CollapsiblePrimitive>

  )
}
