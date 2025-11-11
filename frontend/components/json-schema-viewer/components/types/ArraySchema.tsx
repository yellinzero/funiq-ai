'use client'

import type { JSONSchema } from '../../types'
import { useTranslation } from '@/plugins/i18n/client'
import React, { type FC } from 'react'
import { NestedSchema } from '../../context'
import { SchemaCollapsible } from '../SchemaCollapsible'
import { SchemaProperty } from '../SchemaProperty'
import { SchemaResolver } from '../SchemaResolver'

interface ArraySchemaProps {
  schema: Exclude<JSONSchema, boolean>
  name?: string
  required?: boolean
  level?: number
}

/**
 * Render array type schema
 */
export const ArraySchema: FC<ArraySchemaProps> = ({
  schema,
  name,
  required = false,
  level = 0,
}) => {
  const { t } = useTranslation(['global'])
  const items = schema.items as JSONSchema | undefined
  const prefixItems = schema.prefixItems as JSONSchema[] | undefined
  const contains = schema.contains as JSONSchema | undefined

  return (
    <SchemaProperty
      name={name}
      type="array"
      description={schema.description}
      required={required}
      deprecated={schema.deprecated}
      readOnly={schema.readOnly}
      defaultValue={schema.default}
      level={level}
    >
      {/* Array item type */}
      {items && (
        <div className="mt-2">
          <SchemaCollapsible
            summary={(
              <span className="text-xs font-medium text-muted-foreground">
                {t('global.json_schema.array_items')}
              </span>
            )}
            defaultOpen={level < 2}
            contentClassName="mt-1 border-l-2 border-muted pl-3"
          >
            <NestedSchema jsonPointer="items">
              <SchemaResolver
                schema={items}
                name="item"
                level={level + 1}
              />
            </NestedSchema>
          </SchemaCollapsible>
        </div>
      )}

      {/* Prefix items (tuple) */}
      {prefixItems && prefixItems.length > 0 && (
        <div className="mt-2 border-l-2 border-muted pl-3">
          <div className="mb-2 text-xs font-medium text-muted-foreground">
            {t('global.json_schema.tuple_items')}
            :
          </div>
          <div className="space-y-2">
            {prefixItems.map((itemSchema, index) => (
              <NestedSchema key={index} jsonPointer={`prefixItems/${index}`}>
                <SchemaResolver
                  schema={itemSchema}
                  name={`[${index}]`}
                  level={level + 1}
                />
              </NestedSchema>
            ))}
          </div>
        </div>
      )}

      {/* Contains element */}
      {contains && (
        <div className="mt-2 border-l-2 border-muted pl-3">
          <div className="mb-2 text-xs font-medium text-muted-foreground">
            {t('global.json_schema.must_contain')}
            :
          </div>
          <NestedSchema jsonPointer="contains">
            <SchemaResolver
              schema={contains}
              level={level + 1}
            />
          </NestedSchema>
        </div>
      )}

      {/* Array length and uniqueness constraints */}
      <div className="mt-2 space-y-1 text-xs text-muted-foreground">
        {schema.minItems !== undefined && (
          <div>
            {t('global.json_schema.min_items')}
            :
            {' '}
            {schema.minItems}
          </div>
        )}
        {schema.maxItems !== undefined && (
          <div>
            {t('global.json_schema.max_items')}
            :
            {' '}
            {schema.maxItems}
          </div>
        )}
        {schema.uniqueItems && (
          <div className="text-primary">{t('global.json_schema.unique_items')}</div>
        )}
        {schema.minContains !== undefined && (
          <div>
            {t('global.json_schema.min_contains')}
            :
            {' '}
            {schema.minContains}
          </div>
        )}
        {schema.maxContains !== undefined && (
          <div>
            {t('global.json_schema.max_contains')}
            :
            {' '}
            {schema.maxContains}
          </div>
        )}
      </div>
    </SchemaProperty>
  )
}
