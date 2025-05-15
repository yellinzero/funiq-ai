'use client'

import { createContext, type ReactNode, useContext, useMemo, useState } from 'react'

interface HeaderContent {
  leftContent?: ReactNode
  centerContent?: ReactNode
  rightContent?: ReactNode
}

interface WorkspaceHeaderContextType {
  setHeaderContent: (content: HeaderContent) => void
  headerContent: HeaderContent
  clearHeaderContent: () => void
}

const WorkspaceHeaderContext = createContext<WorkspaceHeaderContextType | null>(null)

export function WorkspaceHeaderProvider({ children }: { children: ReactNode }) {
  const [headerContent, setHeaderContent] = useState<HeaderContent>({})

  const value = useMemo(() => ({
    headerContent,
    setHeaderContent,
    clearHeaderContent: () => setHeaderContent({}),
  }), [headerContent])

  return (
    <WorkspaceHeaderContext.Provider value={value}>
      {children}
    </WorkspaceHeaderContext.Provider>
  )
}

export function useWorkspaceHeader() {
  const context = useContext(WorkspaceHeaderContext)
  if (!context) {
    throw new Error('useWorkspaceHeader must be used within a WorkspaceHeaderProvider')
  }
  return context
}
