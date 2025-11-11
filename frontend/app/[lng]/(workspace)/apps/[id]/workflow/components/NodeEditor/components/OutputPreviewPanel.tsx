'use client'

import { formatJsonData, generateMockDataFromSchema } from '@/app/[lng]/(workspace)/apps/[id]/workflow/utils/schema'
import { cn } from '@/utils/ui'
import { useMemo } from 'react'

interface OutputPanelProps {
  outputSchema?: any
  actualOutput?: any
  hasExecuted?: boolean
}

export function OutputPreviewPanel({ outputSchema, actualOutput, hasExecuted = false }: OutputPanelProps) {
  const mockData = useMemo(() => {
    if (actualOutput !== undefined && actualOutput !== null) {
      return actualOutput
    }
    if (outputSchema) {
      return generateMockDataFromSchema(outputSchema)
    }
    return null
  }, [outputSchema, actualOutput])

  const hasData = mockData !== null

  return (
    <div className="p-4 size-full overflow-auto">
      {hasData
        ? (
            <div className="space-y-2">
              {!hasExecuted && (
                <div className="flex items-center gap-2 px-3 py-2 text-xs bg-amber-500/10 text-amber-700 dark:text-amber-400 rounded border border-amber-500/20 mb-3">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  <span>Example</span>
                </div>
              )}
              <pre className={cn(
                'text-xs font-mono p-3 rounded-md bg-muted/50',
                'overflow-x-auto',
              )}
              >
                {formatJsonData(mockData)}
              </pre>
            </div>
          )
        : (
            <div className="flex flex-col items-center justify-center h-32 text-center">
              <p className="text-sm text-muted-foreground">
                Execute this node to view data
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                or
                {' '}
                <span className="text-primary cursor-pointer hover:underline">
                  set mock data
                </span>
              </p>
            </div>
          )}
    </div>
  )
}
