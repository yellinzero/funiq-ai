'use client'

import type { JSONSchema } from '../types'
import { Button } from '@/components/base/button'
import { useTranslation } from '@/plugins/i18n/client'
import React, { type FC, useState } from 'react'
import { NestedSchema } from '../context'
import { generateFriendlyName } from '../utils'
import { SchemaResolver } from './SchemaResolver'

interface SchemaCompositionProps {
  schema: Exclude<JSONSchema, boolean>
  level?: number
}

/**
 * Render schema composition (anyOf/oneOf/allOf/not)
 */
export const SchemaComposition: FC<SchemaCompositionProps> = ({ schema, level = 0 }) => {
  const [activeTab, setActiveTab] = useState(0)
  const { t } = useTranslation(['global'])

  // anyOf - matches any one of the following
  if (schema.anyOf) {
    return (
      <div className="mt-2 border-l-2 border-orange-500/30 pl-4">
        <div className="mb-2 flex items-center gap-2">
          <span className="rounded bg-orange-500/10 px-2 py-0.5 text-xs font-medium text-orange-600 dark:bg-orange-500/20 dark:text-orange-400">
            {t('global.json_schema.any_of')}
          </span>
          <span className="text-xs text-muted-foreground">{t('global.json_schema.any_of_description')}</span>
        </div>
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            {schema.anyOf.map((subSchema, index) => (
              <Button
                key={index}
                variant={activeTab === index ? 'default' : 'ghost'}
                size="sm"
                className="!p-1 h-auto !text-xs"
                onClick={() => setActiveTab(index)}
              >
                {generateFriendlyName(subSchema)}
              </Button>
            ))}
          </div>
          {schema.anyOf[activeTab] && (
            <NestedSchema jsonPointer={`anyOf/${activeTab}`}>
              <SchemaResolver schema={schema.anyOf[activeTab]} level={level + 1} />
            </NestedSchema>
          )}

        </div>
      </div>
    )
  }

  // oneOf - must match exactly one of the following
  if (schema.oneOf) {
    return (
      <div className="mt-2 border-l-2 border-blue-500/30 pl-4">
        <div className="mb-2 flex items-center gap-2">
          <span className="rounded bg-blue-500/10 px-2 py-0.5 text-xs font-medium text-blue-600 dark:bg-blue-500/20 dark:text-blue-400">
            {t('global.json_schema.one_of')}
          </span>
          <span className="text-xs text-muted-foreground">{t('global.json_schema.one_of_description')}</span>
        </div>
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            {schema.oneOf.map((subSchema, index) => (
              <Button
                key={index}
                variant={activeTab === index ? 'default' : 'ghost'}
                size="sm"
                className="!p-1 h-auto !text-xs"
                onClick={() => setActiveTab(index)}
              >
                {generateFriendlyName(subSchema)}
              </Button>
            ))}
          </div>
          {schema.oneOf[activeTab] && (
            <NestedSchema jsonPointer={`oneOf/${activeTab}`}>
              <SchemaResolver schema={schema.oneOf[activeTab]} level={level + 1} />
            </NestedSchema>
          )}
        </div>
      </div>
    )
  }

  // allOf - must match all of the following
  if (schema.allOf) {
    return (
      <div className="mt-2 border-l-2 border-green-500/30 pl-4">
        <div className="mb-2 flex items-center gap-2">
          <span className="rounded bg-green-500/10 px-2 py-0.5 text-xs font-medium text-green-600 dark:bg-green-500/20 dark:text-green-400">
            {t('global.json_schema.all_of')}
          </span>
          <span className="text-xs text-muted-foreground">{t('global.json_schema.all_of_description')}</span>
        </div>
        <div className="space-y-3">
          {schema.allOf.map((subSchema, index) => (
            <div key={index} className="rounded border border-border/50 p-2">
              <div className="mb-1 text-xs font-medium text-muted-foreground">
                {t('global.json_schema.condition')}
                {' '}
                {index + 1}
              </div>
              <NestedSchema jsonPointer={`allOf/${index}`}>
                <SchemaResolver schema={subSchema} level={level + 1} />
              </NestedSchema>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // not - must not match the following
  if (schema.not) {
    return (
      <div className="mt-2 border-l-2 border-red-500/30 pl-4">
        <div className="mb-2 flex items-center gap-2">
          <span className="rounded bg-red-500/10 px-2 py-0.5 text-xs font-medium text-red-600 dark:bg-red-500/20 dark:text-red-400">
            {t('global.json_schema.not')}
          </span>
          <span className="text-xs text-muted-foreground">{t('global.json_schema.not_description')}</span>
        </div>
        <NestedSchema jsonPointer="not">
          <SchemaResolver schema={schema.not} level={level + 1} />
        </NestedSchema>
      </div>
    )
  }

  return null
}
