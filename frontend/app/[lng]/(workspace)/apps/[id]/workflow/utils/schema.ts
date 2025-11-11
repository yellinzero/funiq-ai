import { faker } from '@faker-js/faker'
import { JSONSchemaFaker } from 'json-schema-faker'

// 配置 json-schema-faker 使用 faker.js
JSONSchemaFaker.extend('faker', () => faker)

/**
 * 根据 JSON Schema 生成示例数据
 */
export function generateMockDataFromSchema(schema: any): any {
  if (!schema)
    return null

  try {
    const jsonSchema = schema.json_schema || schema

    // 使用 json-schema-faker 生成数据
    const mockData = JSONSchemaFaker.generate(jsonSchema)
    return mockData
  }
  catch (error) {
    console.error('Failed to generate mock data from schema:', error)
    // 降级到简单实现
    return generateSimpleMockData(schema)
  }
}

/**
 * 简单的 mock 数据生成 (作为后备)
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
 * 格式化 JSON 数据以便展示
 */
export function formatJsonData(data: any): string {
  try {
    return JSON.stringify(data, null, 2)
  }
  catch {
    return String(data)
  }
}
