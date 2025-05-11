'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

type WorkspaceContextType = {
  activeApp: string | null
  isInApp: boolean
}

const WorkspaceContext = createContext<WorkspaceContextType | null>(null)

export function useWorkspace() {
  const context = useContext(WorkspaceContext)
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider')
  }
  return context
}

export function WorkspaceProvider({
  children
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [activeApp, setActiveApp] = useState<string | null>(() => {
    const match = pathname?.match(/\/apps\/([^\/]+)/)
    return  match?.[1] ?? null
  })

  useEffect(() => {
    const appMatch = pathname?.match(/\/apps\/([^\/]+)/)

    if (appMatch) {
      const newAppId = appMatch[1] ?? null
      setActiveApp(prev => {
        if (prev !== newAppId) {
          return newAppId
        }
        return prev
      })
    } else if (pathname === '/apps') {
      setActiveApp(null)
    } else {
      setActiveApp(null)
    }
  }, [pathname])

  const value = {
    activeApp,
    isInApp: !!activeApp
  }

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  )
}