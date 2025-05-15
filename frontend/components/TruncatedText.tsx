'use client'

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/base/tooltip'
import { cn } from '@/utils/ui'
import { useResizeObserver } from '@reactuses/core'
import * as React from 'react'

interface TruncatedTextProps extends React.HTMLAttributes<HTMLDivElement> {
  text?: string
  lines?: 1 | 2 | 3 | 4 | 5 | 6
  tooltipProps?: React.ComponentProps<typeof TooltipContent>
  enableObserver?: boolean
  disabled?: boolean
  children?: React.ReactNode
}

const lineClampClasses = {
  1: 'truncate',
  2: 'line-clamp-2',
  3: 'line-clamp-3',
  4: 'line-clamp-4',
  5: 'line-clamp-5',
  6: 'line-clamp-6',
} as const

export function TruncatedText({
  text,
  lines = 1,
  tooltipProps,
  enableObserver = false,
  disabled = false,
  className,
  children,
  style,
  ...props
}: TruncatedTextProps) {
  const textRef = React.useRef<HTMLDivElement>(null)
  const [shouldShowTooltip, setShouldShowTooltip] = React.useState(false)
  const [tooltipContent, setTooltipContent] = React.useState<string>('')

  const computeShouldShowTooltip = React.useCallback(() => {
    if (textRef.current) {
      const isHeightOverflow = textRef.current.scrollHeight > textRef.current.clientHeight
      const isWidthOverflow = textRef.current.scrollWidth > textRef.current.clientWidth
      setShouldShowTooltip(isHeightOverflow || isWidthOverflow)
      setTooltipContent(textRef.current.textContent || text || '')
    }
  }, [text])

  React.useEffect(() => {
    computeShouldShowTooltip()
  }, [computeShouldShowTooltip])

  useResizeObserver(textRef, () => {
    if (enableObserver) {
      computeShouldShowTooltip()
    }
  })

  const content = (
    <div
      ref={textRef}
      className={cn(lineClampClasses[lines], className)}
      style={style}
      {...props}
    >
      {children || text}
    </div>
  )

  if (disabled || !shouldShowTooltip) {
    return content
  }

  return (
    <TooltipProvider>
      <Tooltip delayDuration={300}>
        <TooltipTrigger asChild>
          {content}
        </TooltipTrigger>
        <TooltipContent {...tooltipProps}>
          {tooltipContent}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
