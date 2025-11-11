'use client'

import { Button } from '@/components/base/button'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import dynamic from 'next/dynamic'
import { useState } from 'react'

const OutputPreviewPanel = dynamic(() => import('./components/OutputPreviewPanel').then(mod => ({ default: mod.OutputPreviewPanel })), {
  ssr: false,
})

const SchemaDocumentation = dynamic(() => import('./components/SchemaDocumentation').then(mod => ({ default: mod.SchemaDocumentation })), {
  ssr: false,
})

interface RightPanelProps {
  isOpen: boolean
  operatorInfo: any
  actualOutput?: any
  hasExecuted?: boolean
  className?: string
}

export function RightPanel({ isOpen, operatorInfo, actualOutput, hasExecuted = false, className }: RightPanelProps) {
  const { t } = useTranslation(['app'])

  // State to manage which tab is active: preview or schema documentation
  const [outputTab, setOutputTab] = useState<'preview' | 'schema'>('preview')

  return (
    <div className={cn('flex flex-col h-full overflow-hidden', className)}>
      {/* Right panel header */}
      <div className="px-3 py-3 border-b bg-muted/30 flex items-center justify-between">
        <h3 className="font-medium text-sm flex-1 ml-2">{t('global.output')}</h3>
      </div>

      {/* Right panel content */}
      {isOpen && (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tabs for Preview/Schema Documentation */}
          <div className="border-b">
            <div className="flex">
              <Button
                variant="ghost"
                className={cn(
                  'flex-1 rounded-none h-10',
                  outputTab === 'preview'
                    ? 'border-b-2 border-primary text-primary font-medium'
                    : 'text-muted-foreground',
                )}
                onClick={() => setOutputTab('preview')}
              >
                {t('app.output_data')}
              </Button>
              <Button
                variant="ghost"
                className={cn(
                  'flex-1 rounded-none h-10',
                  outputTab === 'schema'
                    ? 'border-b-2 border-primary text-primary font-medium'
                    : 'text-muted-foreground',
                )}
                onClick={() => setOutputTab('schema')}
              >
                {t('app.schema_documentation')}
              </Button>
            </div>
          </div>

          {/* Content area */}
          <div className="flex-1 overflow-hidden">
            {outputTab === 'preview'
              ? (
                  <OutputPreviewPanel
                    outputSchema={operatorInfo.output_schema}
                    actualOutput={actualOutput}
                    hasExecuted={hasExecuted}
                  />
                )
              : (
                  <SchemaDocumentation schema={operatorInfo.output_schema} />
                )}
          </div>
        </div>
      )}
    </div>
  )
}
