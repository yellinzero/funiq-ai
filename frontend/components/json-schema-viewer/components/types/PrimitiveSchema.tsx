'use client'

import type { JSONSchema } from '../../types'
import React, { type FC } from 'react'
import { SchemaProperty } from '../SchemaProperty'

interface PrimitiveSchemaProps {
  schema: Exclude<JSONSchema, boolean>
  name?: string
  required?: boolean
  level?: number
}

/**
 *  Render the schema for primitive types (boolean, null)
 */
export const PrimitiveSchema: FC<PrimitiveSchemaProps> = ({
  schema,
  name,
  required = false,
  level = 0,
}) => {
  const type = schema.type === 'boolean' ? 'boolean' : 'null'

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
