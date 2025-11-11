'use client'

import type { JSONSchemaType } from '../types'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import React, { type FC } from 'react'
import { getTypeColorClass } from '../utils'

interface SchemaPropertyProps {
  name?: string
  type?: JSONSchemaType | JSONSchemaType[]
  description?: string
  required?: boolean
  deprecated?: boolean
  readOnly?: boolean
  defaultValue?: any
  enumValues?: readonly any[]
  level?: number
  children?: React.ReactNode
}

/**
 * Render basic information for a single schema property
 */
export const SchemaProperty: FC<SchemaPropertyProps> = ({
  name,
  type,
  description,
  required = false,
  deprecated = false,
  readOnly = false,
  defaultValue,
  enumValues,
  level = 0,
  children,
}) => {
  const { t } = useTranslation(['global'])
  const indent = level * 4

  const renderType = () => {
    if (!type)
      return null

    const types = Array.isArray(type) ? type : [type]

    return (
      <div className="flex flex-wrap gap-1">
        {types.map(t => (
          <span
            key={`${name}-${t}`}
            className={cn(
              'rounded px-1.5 py-0.5 text-xs font-mono',
              getTypeColorClass(t),
            )}
          >
            {t}
          </span>
        ))}
      </div>
    )
  }

  return (
    <div className="mb-3" style={{ paddingLeft: `${indent}px` }}>
      <div className="mb-1 flex flex-wrap items-center gap-2">
        {name && (
          <code className="text-sm font-mono font-medium text-primary">
            {name}
          </code>
        )}

        {renderType()}

        {required && (
          <span className="rounded bg-red-500/10 px-1.5 py-0.5 text-xs text-red-600 dark:bg-red-500/20 dark:text-red-400">
            {t('global.required')}
          </span>
        )}

        {deprecated && (
          <span className="rounded bg-yellow-500/10 px-1.5 py-0.5 text-xs text-yellow-600 dark:bg-yellow-500/20 dark:text-yellow-400">
            {t('global.json_schema.deprecated')}
          </span>
        )}

        {readOnly && (
          <span className="rounded bg-gray-500/10 px-1.5 py-0.5 text-xs text-gray-600 dark:bg-gray-500/20 dark:text-gray-400">
            {t('global.json_schema.read_only')}
          </span>
        )}
      </div>

      {description && (
        <p className="mb-2 text-sm text-muted-foreground">{description}</p>
      )}

      {enumValues && enumValues.length > 0 && (
        <div className="mb-2 text-xs text-muted-foreground">
          <span className="font-medium">
            {t('global.json_schema.enum_values')}
            :
            {' '}
          </span>
          <div className="mt-1 flex flex-wrap gap-1">
            {enumValues.map(val => (
              <code
                key={`${name}-${val}`}
                className="rounded bg-muted px-1.5 py-0.5"
              >
                {JSON.stringify(val)}
              </code>
            ))}
          </div>
        </div>
      )}

      {defaultValue !== undefined && (
        <div className="mb-2 text-xs text-muted-foreground">
          <span className="font-medium">
            {t('global.json_schema.default_value')}
            :
            {' '}
          </span>
          <code className="rounded bg-muted px-1.5 py-0.5">
            {JSON.stringify(defaultValue)}
          </code>
        </div>
      )}

      {children}
    </div>
  )
}
