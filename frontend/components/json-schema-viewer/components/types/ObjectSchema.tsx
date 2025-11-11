'use client'

import type { JSONSchema } from '../../types'
import { useTranslation } from '@/plugins/i18n/client'
import React, { type FC } from 'react'
import { NestedSchema } from '../../context'
import { isRequired } from '../../utils'
import { SchemaCollapsible } from '../SchemaCollapsible'
import { SchemaProperty } from '../SchemaProperty'
import { SchemaResolver } from '../SchemaResolver'

interface ObjectSchemaProps {
  schema: Exclude<JSONSchema, boolean>
  name?: string
  required?: boolean
  level?: number
}

/**
 * Render object type schema
 */
export const ObjectSchema: FC<ObjectSchemaProps> = ({
  schema,
  name,
  required = false,
  level = 0,
}) => {
  const { t } = useTranslation(['global'])
  const properties = schema.properties as Record<string, JSONSchema> | undefined
  const additionalProperties = schema.additionalProperties as boolean | JSONSchema | undefined
  const patternProperties = schema.patternProperties as Record<string, JSONSchema> | undefined
  const hasProperties = properties && Object.keys(properties).length > 0

  return (
    <SchemaProperty
      name={name}
      type="object"
      description={schema.description}
      required={required}
      deprecated={schema.deprecated}
      readOnly={schema.readOnly}
      defaultValue={schema.default}
      level={level}
    >
      {/* Properties list */}
      {hasProperties && (
        <div className="mt-2">
          <SchemaCollapsible
            summary={(
              <span className="text-xs font-medium text-muted-foreground">
                {t('global.json_schema.properties')}
                {' '}
                (
                {Object.keys(properties).length}
                )
              </span>
            )}
            defaultOpen={level < 2}
            contentClassName="mt-1 space-y-1 border-l-2 border-muted pl-3"
          >
            {Object.entries(properties).map(([propName, propSchema]) => (
              <NestedSchema key={propName} jsonPointer={`properties/${propName}`}>
                <SchemaResolver
                  schema={propSchema}
                  name={propName}
                  required={isRequired(propName, schema)}
                  level={level + 1}
                />
              </NestedSchema>
            ))}
          </SchemaCollapsible>
        </div>
      )}

      {/* Additional properties */}
      {additionalProperties !== undefined && additionalProperties !== false && (
        <div className="mt-2 space-y-1 border-l-2 border-muted pl-3">
          <div className="mb-2 text-xs font-medium text-muted-foreground">
            {t('global.json_schema.additional_properties')}
            :
          </div>
          {typeof additionalProperties === 'boolean'
            ? (
                <div className="text-sm text-muted-foreground">
                  {t('global.json_schema.allow_any_additional')}
                </div>
              )
            : (
                <NestedSchema jsonPointer="additionalProperties">
                  <SchemaResolver
                    schema={additionalProperties}
                    name="<additional>"
                    level={level + 1}
                  />
                </NestedSchema>
              )}
        </div>
      )}

      {/* Pattern properties */}
      {patternProperties && Object.keys(patternProperties).length > 0 && (
        <div className="mt-2 space-y-1 border-l-2 border-muted pl-3">
          <div className="mb-2 text-xs font-medium text-muted-foreground">
            {t('global.json_schema.pattern_properties')}
            :
          </div>
          {Object.entries(patternProperties).map(([pattern, propSchema]) => (
            <NestedSchema key={pattern} jsonPointer={`patternProperties/${pattern}`}>
              <div className="mb-2">
                <div className="mb-1 text-xs text-muted-foreground">
                  {t('global.json_schema.match_pattern')}
                  :
                  {' '}
                  <code className="rounded bg-muted px-1 py-0.5">{pattern}</code>
                </div>
                <SchemaResolver
                  schema={propSchema}
                  level={level + 1}
                />
              </div>
            </NestedSchema>
          ))}
        </div>
      )}

      {/* Property count constraints */}
      {(schema.minProperties !== undefined || schema.maxProperties !== undefined) && (
        <div className="mt-2 text-xs text-muted-foreground">
          {schema.minProperties !== undefined && (
            <div>
              {t('global.json_schema.min_properties')}
              :
              {' '}
              {schema.minProperties}
            </div>
          )}
          {schema.maxProperties !== undefined && (
            <div>
              {t('global.json_schema.max_properties')}
              :
              {' '}
              {schema.maxProperties}
            </div>
          )}
        </div>
      )}
    </SchemaProperty>
  )
}
