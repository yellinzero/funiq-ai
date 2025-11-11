'use client'

import type { JSONSchema } from '../../types'
import { useTranslation } from '@/plugins/i18n/client'
import React, { type FC } from 'react'
import { SchemaProperty } from '../SchemaProperty'

interface StringSchemaProps {
  schema: Exclude<JSONSchema, boolean>
  name?: string
  required?: boolean
  level?: number
}

/**
 * Render string type schema
 */
export const StringSchema: FC<StringSchemaProps> = ({
  schema,
  name,
  required = false,
  level = 0,
}) => {
  const { t } = useTranslation(['global'])

  return (
    <SchemaProperty
      name={name}
      type="string"
      description={schema.description}
      required={required}
      deprecated={schema.deprecated}
      readOnly={schema.readOnly}
      defaultValue={schema.default}
      enumValues={schema.enum}
      level={level}
    >
      <div className="mt-2 space-y-1 text-xs text-muted-foreground">
        {schema.format && (
          <div>
            {t('global.json_schema.format')}
            :
            {' '}
            <code className="rounded bg-muted px-1.5 py-0.5">{schema.format}</code>
          </div>
        )}
        {schema.pattern && (
          <div>
            {t('global.json_schema.pattern')}
            :
            {' '}
            <code className="rounded bg-muted px-1.5 py-0.5">{schema.pattern}</code>
          </div>
        )}
        {schema.minLength !== undefined && (
          <div>
            {t('global.json_schema.min_length')}
            :
            {' '}
            {schema.minLength}
          </div>
        )}
        {schema.maxLength !== undefined && (
          <div>
            {t('global.json_schema.max_length')}
            :
            {' '}
            {schema.maxLength}
          </div>
        )}
      </div>
    </SchemaProperty>
  )
}
