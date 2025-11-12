import { faker } from '@faker-js/faker'
import { JSONSchemaFaker } from 'json-schema-faker'

// Configure json-schema-faker to use faker.js
JSONSchemaFaker.extend('faker', () => faker)

/**
 * Generate mock data from a JSON Schema
 */
export function generateMockDataFromSchema(schema: any): any {
  if (!schema)
    return null

  try {
    const jsonSchema = schema.json_schema || schema
    // Use json-schema-faker to generate data
    const mockData = JSONSchemaFaker.generate(jsonSchema)
    return mockData
  }
  catch (error) {
    console.error('Failed to generate mock data from schema:', error)
    // Fallback to a simple mock data generator
    return generateSimpleMockData(schema)
  }
}

/**
 * Simple mock data generator (fallback)
 */
function generateSimpleMockData(schema: any): any {
  const jsonSchema = schema.json_schema || schema

  switch (jsonSchema.type) {
    case 'string':
      if (jsonSchema.enum && jsonSchema.enum.length > 0) {
        return jsonSchema.enum[0]
      }
      return jsonSchema.title || jsonSchema.description || 'example string'

    case 'number':
    case 'integer':
      if (jsonSchema.minimum !== undefined) {
        return jsonSchema.minimum
      }
      if (jsonSchema.maximum !== undefined) {
        return jsonSchema.maximum
      }
      return jsonSchema.type === 'integer' ? 42 : 3.14

    case 'boolean':
      return true

    case 'array':
      if (jsonSchema.items) {
        return [generateSimpleMockData(jsonSchema.items)]
      }
      return []

    case 'object':
      if (jsonSchema.properties) {
        const result: Record<string, any> = {}
        Object.entries(jsonSchema.properties).forEach(([key, propSchema]) => {
          result[key] = generateSimpleMockData(propSchema)
        })
        return result
      }
      return {}

    case 'null':
      return null

    default:
      return null
  }
}

/**
 * Format JSON data for display
 */
export function formatJsonData(data: any): string {
  try {
    return JSON.stringify(data, null, 2)
  }
  catch {
    return String(data)
  }
}
