'use client'

import { formatJsonData } from '@/app/[lng]/(workspace)/apps/[id]/workflow/utils/schema'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'

interface InputPanelProps {
  upstreamNodeName?: string
  inputData?: any
}

export function InputPanel({ upstreamNodeName, inputData }: InputPanelProps) {
  const { t } = useTranslation(['app'])
  const hasData = inputData !== undefined && inputData !== null

  return (
    <div className="flex flex-col size-full">
      {upstreamNodeName && (
        <div className="px-4 py-3 border-b bg-muted/30">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-xs text-muted-foreground">{upstreamNodeName}</span>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-auto">
        <div className="p-4">
          {hasData
            ? (
                <div className="space-y-2">
                  <pre className={cn(
                    'text-xs font-mono p-3 rounded-md bg-muted/50',
                    'overflow-x-auto',
                  )}
                  >
                    {formatJsonData(inputData)}
                  </pre>
                </div>
              )
            : (
                <div className="flex flex-col items-center justify-center h-32 text-center">
                  <p className="text-sm text-muted-foreground">{t('app.text.no_output_data')}</p>
                </div>
              )}
        </div>
      </div>
    </div>
  )
}
