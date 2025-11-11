'use client'

import type { JSONSchema } from './types'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import { Code2, Eye } from 'lucide-react'
import React, { type FC, useState } from 'react'
import { Button } from '../base/button'
import { SchemaResolver } from './components/SchemaResolver'
import { createSchemaContext, SchemaProvider } from './context'

export interface JsonSchemaViewerProps {
  /**
   * JSON Schema object
   */
  schema: JSONSchema
  /**
   * Root title (optional)
   */
  title?: string
  /**
   * Custom class name
   */
  className?: string
  /**
   * Whether to expand by default
   */
  defaultExpanded?: boolean
  /**
   * Whether to show view mode toggle
   */
  showViewToggle?: boolean
  /**
   * Default view mode
   */
  defaultViewMode?: 'visual' | 'json'
  bodyClassName?: string
}

type ViewMode = 'visual' | 'json'

/**
 * JSON Schema viewer component
 * Supports a full range of JSON Schema features, including:
 * - $defs / definitions references
 * - composition: anyOf / oneOf / allOf / not
 * - conditionals: if / then / else
 * - all primitive types and constraints
 */
export const JsonSchemaViewer: FC<JsonSchemaViewerProps> = ({
  schema,
  title,
  className,
  bodyClassName,
  showViewToggle = true,
  defaultViewMode = 'visual',
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>(defaultViewMode)

  // create schema context
  const context = createSchemaContext(schema)

  const { t } = useTranslation(['global'])

  // handle boolean schema
  if (typeof schema === 'boolean') {
    return (
      <div className={className}>
        <div className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground">
          {schema ? t('global.json_schema.any_value_allowed') : t('global.json_schema.no_value_allowed')}
        </div>
      </div>
    )
  }

  const schemaTitle = title || schema.title || 'Schema'

  return (
    <SchemaProvider value={context}>
      <div className={className}>
        <div className="rounded-lg border border-border bg-card">
          {/* Header */}
          <div className="flex items-start justify-between border-b border-border bg-muted/50 px-4 py-3">
            <div className="flex-1">
              <h3 className="text-base font-semibold">{schemaTitle}</h3>
              {schema.description && (
                <p className="mt-1 text-sm text-muted-foreground">
                  {schema.description}
                </p>
              )}
            </div>

            {/* View toggle buttons */}
            {showViewToggle && (
              <>
                {viewMode !== 'visual' && <Button variant="outline" size="icon" onClick={() => setViewMode('visual')}><Eye className="size-3.5" /></Button>}
                {viewMode !== 'json' && <Button variant="outline" size="icon" onClick={() => setViewMode('json')}><Code2 className="size-3.5" /></Button>}
              </>
            )}
          </div>

          {/* Schema content */}

          {viewMode === 'visual'
            ? (
                <div className={cn('p-4', bodyClassName)}>
                  <SchemaResolver schema={schema} />
                </div>
              )
            : (
                <div className={cn('p-2', bodyClassName)}>
                  <textarea
                    className="size-full min-h-[400px] resize-y rounded-md border border-border bg-muted/30 p-3 font-mono text-xs"
                    value={JSON.stringify(schema, null, 2)}
                    readOnly
                  />
                </div>
              )}

        </div>
      </div>
    </SchemaProvider>
  )
}
