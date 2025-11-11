'use client'

import type { JSONSchema } from '../../types'
import { useTranslation } from '@/plugins/i18n/client'
import React, { type FC } from 'react'
import { SchemaProperty } from '../SchemaProperty'

interface NumberSchemaProps {
  schema: Exclude<JSONSchema, boolean>
  name?: string
  required?: boolean
  level?: number
}

/**
 * Render number/integer type schema
 */
export const NumberSchema: FC<NumberSchemaProps> = ({
  schema,
  name,
  required = false,
  level = 0,
}) => {
  const { t } = useTranslation(['global'])
  const type = schema.type === 'integer' ? 'integer' : 'number'

  return (
    <SchemaProperty
      name={name}
      type={type}
      description={schema.description}
      required={required}
      deprecated={schema.deprecated}
      readOnly={schema.readOnly}
      defaultValue={schema.default}
      enumValues={schema.enum}
      level={level}
    >
      <div className="mt-2 space-y-1 text-xs text-muted-foreground">
        {schema.minimum !== undefined && (
          <div>
            {t('global.json_schema.minimum')}
            :
            {' '}
            {schema.minimum}
            {' '}
            (
            {t('global.json_schema.inclusive')}
            )
          </div>
        )}
        {schema.maximum !== undefined && (
          <div>
            {t('global.json_schema.maximum')}
            :
            {' '}
            {schema.maximum}
            {' '}
            (
            {t('global.json_schema.inclusive')}
            )
          </div>
        )}
        {schema.exclusiveMinimum !== undefined && (
          <div>
            {t('global.json_schema.exclusive_minimum')}
            :
            {' '}
            {schema.exclusiveMinimum}
            {' '}
            (
            {t('global.json_schema.exclusive')}
            )
          </div>
        )}
        {schema.exclusiveMaximum !== undefined && (
          <div>
            {t('global.json_schema.exclusive_maximum')}
            :
            {' '}
            {schema.exclusiveMaximum}
            {' '}
            (
            {t('global.json_schema.exclusive')}
            )
          </div>
        )}
        {schema.multipleOf !== undefined && (
          <div>
            {t('global.json_schema.must_be_multiple')}
            {' '}
            {schema.multipleOf}
          </div>
        )}
      </div>
    </SchemaProperty>
  )
}
