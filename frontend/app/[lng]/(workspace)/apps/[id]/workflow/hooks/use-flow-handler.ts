import type { IOperatorEntity } from '@/apis'
import { nanoid } from '@/app/[lng]/(workspace)/apps/[id]/workflow/utils/workflow'
import { type Connection, type Edge, getOutgoers, type Node, useReactFlow } from '@xyflow/react'
import { useCallback } from 'react'

export function useFlowHandler() {
  const { screenToFlowPosition, addNodes, getNodes, getEdges } = useReactFlow()

  const createNode = useCallback((operator: IOperatorEntity) => {
    const centerPosition = screenToFlowPosition({
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    })

    const nodeKey = nanoid()
    const newNode = {
      id: nodeKey,
      type: operator.name,
      position: centerPosition,
      data: {
        id: null,
        operator: operator.name,
        name: `${operator.name}-${nodeKey}`,
        description: '',
        config: null,
        extended_config: null,
      },
    }

    addNodes(newNode)
  }, [addNodes, screenToFlowPosition])

  const isValidConnection = useCallback(
    (connection: Edge | Connection) => {
      const nodes = getNodes()
      const edges = getEdges()
      const target = nodes.find(node => node.id === connection.target)
      if (!target)
        return false

      const hasCycle = (node: Node, visited = new Set()) => {
        if (visited.has(node.id))
          return false

        visited.add(node.id)

        for (const outgoer of getOutgoers(node, nodes, edges)) {
          if (outgoer.id === connection.source)
            return true
          if (hasCycle(outgoer, visited))
            return true
        }
      }

      if (target.id === connection.source)
        return false
      return !hasCycle(target)
    },
    [getNodes, getEdges],
  )

  return {
    createNode,
    isValidConnection,
  }
}
