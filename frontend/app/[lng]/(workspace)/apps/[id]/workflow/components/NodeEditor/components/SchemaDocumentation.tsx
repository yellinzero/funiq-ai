'use client'

import { JsonSchemaViewer } from '@/components/json-schema-viewer/JsonSchemaViewer'
import { useTranslation } from '@/plugins/i18n/client'

interface SchemaDocumentationProps {
  schema: Record<string, any> | null
}

export function SchemaDocumentation({ schema }: SchemaDocumentationProps) {
  const { t } = useTranslation(['app'])

  if (!schema) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
        {t('app.text.no_schema_definition')}
      </div>
    )
  }

  const jsonSchema = schema.json_schema || schema

  return (
    <div className="size-full overflow-auto p-4">
      <JsonSchemaViewer
        schema={jsonSchema}
        title={t('app.output_data_structure')}
      />
    </div>
  )
}
