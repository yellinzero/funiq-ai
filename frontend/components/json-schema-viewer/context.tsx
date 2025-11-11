'use client'

import type { JSONSchema, SchemaViewerContext } from './types'
import React, { createContext, type FC, type ReactNode, useContext } from 'react'
import { getDefs } from './utils'

const SchemaContext = createContext<SchemaViewerContext | null>(null)

interface SchemaProviderProps {
  value: SchemaViewerContext
  children: ReactNode
}

export const SchemaProvider: FC<SchemaProviderProps> = ({ value, children }) => {
  return <SchemaContext.Provider value={value}>{children}</SchemaContext.Provider>
}

export function useSchemaContext(): SchemaViewerContext {
  const context = useContext(SchemaContext)
  if (!context) {
    throw new Error('useSchemaContext must be used within SchemaProvider')
  }
  return context
}

interface NestedSchemaProps {
  jsonPointer: string
  children: ReactNode
}

export const NestedSchema: FC<NestedSchemaProps> = ({ jsonPointer, children }) => {
  const parentContext = useSchemaContext()

  const newContext: SchemaViewerContext = {
    ...parentContext,
    jsonPointer,
    level: parentContext.level + 1,
  }

  return <SchemaProvider value={newContext}>{children}</SchemaProvider>
}

export function createSchemaContext(schema: JSONSchema): SchemaViewerContext {
  return {
    fullSchema: schema,
    jsonPointer: '',
    level: 0,
    defs: getDefs(schema),
  }
}
