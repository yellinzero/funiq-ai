import type { JSONSchema, JSONSchemaType } from './types'

/**
 * Detect the schema type
 */
export function detectSchemaType(schema: JSONSchema): JSONSchemaType | JSONSchemaType[] | undefined {
  if (typeof schema === 'boolean')
    return undefined

  return schema.type as JSONSchemaType | JSONSchemaType[] | undefined
}

/**
 * Check whether the schema is a composition (anyOf / oneOf / allOf / not)
 */
export function isSchemaComposition(schema: JSONSchema): boolean {
  if (typeof schema === 'boolean')
    return false

  return !!(schema.anyOf || schema.oneOf || schema.allOf || schema.not)
}

/**
 * Check whether the schema is conditional (if / then / else / dependentSchemas / dependentRequired)
 */
export function isSchemaConditional(schema: JSONSchema): boolean {
  if (typeof schema === 'boolean')
    return false

  return !!(schema.if || schema.dependentSchemas || schema.dependentRequired)
}

/**
 * Check whether the schema contains $defs / definitions
 */
export function hasDefs(schema: JSONSchema): boolean {
  if (typeof schema === 'boolean')
    return false

  return !!(schema.$defs || schema.definitions)
}

/**
 * Get $defs / definitions from the schema
 */
export function getDefs(schema: JSONSchema): Record<string, JSONSchema> | undefined {
  if (typeof schema === 'boolean')
    return undefined

  return schema.$defs || schema.definitions
}

/**
 * Resolve a $ref reference.
 * Supported forms:
 * - #/$defs/DefinitionName
 * - #/definitions/DefinitionName
 * - #/properties/propertyName
 */
export function resolveRef(ref: string, fullSchema: JSONSchema, defs?: Record<string, JSONSchema>): JSONSchema | null {
  if (!ref.startsWith('#/'))
    return null

  const path = ref.slice(2).split('/')

  if (path[0] === '$defs' || path[0] === 'definitions') {
    const defName = path[1]
    if (defs && defName && defs[defName]) {
      return defs[defName]
    }
  }

  let current: any = fullSchema
  for (const segment of path) {
    if (current && typeof current === 'object' && segment in current) {
      current = current[segment]
    }
    else {
      return null
    }
  }

  return current as JSONSchema
}

/**
 * Generate a friendly name for a schema (title, type, enum, const, or fallback)
 */
export function generateFriendlyName(schema: JSONSchema): string {
  if (typeof schema === 'boolean') {
    return schema ? 'Any' : 'Never'
  }

  if (schema.title)
    return String(schema.title)

  if (schema.type) {
    if (Array.isArray(schema.type)) {
      return schema.type.join(' | ')
    }
    return String(schema.type)
  }

  if (schema.enum) {
    return 'enum'
  }

  if (schema.const !== undefined) {
    return 'const'
  }

  return 'Schema'
}

/**
 * Format a JSON Pointer segment (escape ~ and / as ~0 and ~1)
 */
export function formatJsonPointer(pointer: string): string {
  return pointer.replace(/~/g, '~0').replace(/\//g, '~1')
}

/**
 * Append a segment to a base JSON Pointer, escaping the segment
 */
export function appendJsonPointer(base: string, segment: string): string {
  const formattedSegment = formatJsonPointer(segment)
  return `${base}/${formattedSegment}`
}

/**
 * Check whether a field is required in a parent schema
 */
export function isRequired(fieldName: string, parentSchema: JSONSchema): boolean {
  if (typeof parentSchema === 'boolean')
    return false

  return parentSchema.required?.includes(fieldName) ?? false
}

/**
 * Get the CSS class names for a given JSON Schema type (used for color styling)
 */
export function getTypeColorClass(type: JSONSchemaType): string {
  const colorMap: Record<JSONSchemaType, string> = {
    string: 'bg-blue-500/10 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400',
    number: 'bg-green-500/10 text-green-600 dark:bg-green-500/20 dark:text-green-400',
    integer: 'bg-green-500/10 text-green-600 dark:bg-green-500/20 dark:text-green-400',
    boolean: 'bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400',
    array: 'bg-orange-500/10 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400',
    object: 'bg-pink-500/10 text-pink-600 dark:bg-pink-500/20 dark:text-pink-400',
    null: 'bg-gray-500/10 text-gray-600 dark:bg-gray-500/20 dark:text-gray-400',
  }

  return colorMap[type] || 'bg-gray-500/10 text-gray-600 dark:bg-gray-500/20 dark:text-gray-400'
}
