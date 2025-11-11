import type { JSONSchema as JSONSchemaNS, TypeName } from 'json-schema-typed'

// I'm only interested with the values behind that enum
export type { keywords } from 'json-schema-typed'

/**
 * JSON Schema types definitions
 */
export type JSONSchemaType = `${TypeName}`

export type JSONSchema = JSONSchemaNS

export interface SchemaViewerContext {
  // full schema, used for resolving $ref
  fullSchema: JSONSchema
  // current json pointer path
  jsonPointer: string
  // level of nesting
  level: number
  // $defs
  defs?: Record<string, JSONSchema>
}
