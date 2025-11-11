'use client'

import type { JSONSchema } from '../types'
import { useTranslation } from '@/plugins/i18n/client'
import React, { type FC } from 'react'
import { detectSchemaType, isSchemaComposition } from '../utils'
import { SchemaComposition } from './SchemaComposition'
import { SchemaProperty } from './SchemaProperty'
import { ArraySchema } from './types/ArraySchema'
import { NumberSchema } from './types/NumberSchema'
import { ObjectSchema } from './types/ObjectSchema'
import { PrimitiveSchema } from './types/PrimitiveSchema'
import { StringSchema } from './types/StringSchema'

interface SchemaRendererProps {
  schema: Exclude<JSONSchema, boolean>
  name?: string
  required?: boolean
  level?: number
}

/**
 * Select the appropriate rendering component based on schema type
 */
export const SchemaRenderer: FC<SchemaRendererProps> = ({
  schema,
  name,
  required = false,
  level = 0,
}) => {
  const { t } = useTranslation(['global'])

  // Check if this is a composition schema
  const isComposition = isSchemaComposition(schema)

  // Handle const value
  if ('const' in schema && schema.const !== undefined) {
    return (
      <SchemaProperty
        name={name}
        description={schema.description}
        required={required}
        level={level}
      >
        <div className="text-xs text-muted-foreground">
          {t('global.json_schema.const_value')}
          :
          {' '}
          <code className="rounded bg-muted px-1.5 py-0.5">
            {JSON.stringify(schema.const)}
          </code>
        </div>
      </SchemaProperty>
    )
  }

  // Detect type
  const type = detectSchemaType(schema)

  // Render main type content
  const renderTypeContent = () => {
    if (!type) {
      // No explicit type, but may have other constraints
      return (
        <SchemaProperty
          name={name}
          description={schema.description}
          required={required}
          deprecated={schema.deprecated}
          readOnly={schema.readOnly}
          defaultValue={schema.default}
          level={level}
        />
      )
    }

    // Handle multiple types
    if (Array.isArray(type)) {
      return (
        <SchemaProperty
          name={name}
          type={type}
          description={schema.description}
          required={required}
          deprecated={schema.deprecated}
          readOnly={schema.readOnly}
          defaultValue={schema.default}
          level={level}
        />
      )
    }

    // Select rendering component based on single type
    switch (type) {
      case 'object':
        return (
          <ObjectSchema
            schema={schema}
            name={name}
            required={required}
            level={level}
          />
        )
      case 'array':
        return (
          <ArraySchema
            schema={schema}
            name={name}
            required={required}
            level={level}
          />
        )
      case 'string':
        return (
          <StringSchema
            schema={schema}
            name={name}
            required={required}
            level={level}
          />
        )
      case 'number':
      case 'integer':
        return (
          <NumberSchema
            schema={schema}
            name={name}
            required={required}
            level={level}
          />
        )
      case 'boolean':
      case 'null':
        return (
          <PrimitiveSchema
            schema={schema}
            name={name}
            required={required}
            level={level}
          />
        )
      default:
        return (
          <SchemaProperty
            name={name}
            type={type}
            description={schema.description}
            required={required}
            level={level}
          />
        )
    }
  }

  return (
    <>
      {renderTypeContent()}
      {isComposition && <SchemaComposition schema={schema} level={level} />}
    </>
  )
}
