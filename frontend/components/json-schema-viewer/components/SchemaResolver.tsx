'use client'

import type { JSONSchema } from '../types'
import { useTranslation } from '@/plugins/i18n/client'
import React, { type FC } from 'react'
import { useSchemaContext } from '../context'
import { resolveRef } from '../utils'
import { SchemaRenderer } from './SchemaRenderer'

interface SchemaResolverProps {
  schema: JSONSchema
  name?: string
  required?: boolean
  level?: number
}

/**
 * Resolve and render schema, handling $ref references
 */
export const SchemaResolver: FC<SchemaResolverProps> = ({
  schema,
  name,
  required = false,
  level = 0,
}) => {
  const context = useSchemaContext()
  const { t } = useTranslation(['global'])

  // Handle boolean schema
  if (typeof schema === 'boolean') {
    return (
      <div className="text-sm text-muted-foreground">
        {schema ? t('global.json_schema.any_value_allowed') : t('global.json_schema.no_value_allowed')}
      </div>
    )
  }

  // Handle $ref references
  if ('$ref' in schema && schema.$ref) {
    const resolved = resolveRef(schema.$ref, context.fullSchema, context.defs)

    if (!resolved) {
      return (
        <div className="text-sm text-destructive">
          {t('global.json_schema.unable_to_resolve_ref')}
          :
          {' '}
          {schema.$ref}
        </div>
      )
    }

    // Recursively render resolved schema
    return (
      <SchemaResolver
        schema={resolved}
        name={name}
        required={required}
        level={level}
      />
    )
  }

  // Render normal schema
  return (
    <SchemaRenderer
      schema={schema}
      name={name}
      required={required}
      level={level}
    />
  )
}
