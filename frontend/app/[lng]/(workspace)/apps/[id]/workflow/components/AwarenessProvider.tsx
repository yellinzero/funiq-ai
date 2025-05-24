'use client'

import { useWorkflowStore } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import { useCurrentUser } from '@/app/[lng]/stores/use-global-store'
import { useDebounceFn } from '@reactuses/core'
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

export interface UserPresence {
  id: string
  name: string
  color: string
  selectedNodes?: string[]
}

interface AwarenessContextType {
  onlineUsers: Map<number, UserPresence>
  handleNodesSelect: (nodeIds: string[]) => void
  currentClientId?: number
}

const AwarenessContext = createContext<AwarenessContextType | null>(null)

export function AwarenessProvider({ children }: { children: React.ReactNode }) {
  const currentUser = useCurrentUser()
  const { wsProvider, ydoc } = useWorkflowStore()
  const [onlineUsers, setOnlineUsers] = useState<Map<number, UserPresence>>(new Map())

  const { run: debouncedSetLocalState } = useDebounceFn((awareness: any, state: any) => {
    awareness.setLocalState(state)
  }, 100)

  const handleNodesSelect = useCallback((nodeIds: string[]) => {
    const awareness = wsProvider?.awareness
    if (!awareness)
      return

    const currentState = awareness.getLocalState()
    if (currentState) {
      debouncedSetLocalState(awareness, {
        ...currentState,
        selectedNodes: nodeIds,
      })
    }
  }, [wsProvider, debouncedSetLocalState])

  const contextValue = useMemo(() => ({
    onlineUsers,
    handleNodesSelect,
    currentClientId: ydoc?.clientID,
  }), [onlineUsers, handleNodesSelect, ydoc?.clientID])

  useEffect(() => {
    const awareness = wsProvider?.awareness
    if (!awareness || !currentUser)
      return

    // 设置初始状态
    awareness.setLocalState({
      id: currentUser.id,
      name: currentUser.name,
      color: `#${Math.floor(Number.parseInt(currentUser.id.slice(0, 8), 16) % 0xFFFFFF).toString(16).padStart(6, '0')}`,
      selectedNodes: [],
    })

    const handleAwarenessChange = () => {
      const states = Array.from(awareness.getStates().entries())
      const newOnlineUsers = new Map<number, UserPresence>()
      states.forEach(([clientId, state]) => {
        if (state) {
          newOnlineUsers.set(clientId, state as UserPresence)
        }
      })
      setOnlineUsers(newOnlineUsers)
    }

    awareness.on('change', handleAwarenessChange)
    return () => {
      awareness.off('change', handleAwarenessChange)
      debouncedSetLocalState.cancel()
    }
  }, [wsProvider, currentUser, debouncedSetLocalState])

  return (
    <AwarenessContext.Provider value={contextValue}>
      {children}
    </AwarenessContext.Provider>
  )
}

export function useAwareness() {
  const context = useContext(AwarenessContext)
  if (!context) {
    throw new Error('useAwareness must be used within an AwarenessProvider')
  }
  return context
}
