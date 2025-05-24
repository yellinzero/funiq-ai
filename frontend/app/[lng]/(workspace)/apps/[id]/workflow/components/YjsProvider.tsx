import type { WorkflowEdge, WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import { type IWorkflowInfo, updateWorkflowApi } from '@/apis'
import { useWorkflowStore } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import { normalizeWorkflowEdge, normalizeWorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/utils'
import { useDebounceFn } from '@reactuses/core'
import * as _ from 'lodash-es'
import { useEffect, useRef } from 'react'
import { WebsocketProvider } from 'y-websocket'
import * as Y from 'yjs'

export function YjsProvider({
  children,
  workflowId,
}: {
  children: React.ReactNode
  workflowId: string
}) {
  const isInitializing = useRef(true)

  const { run: saveWorkflowConfig } = useDebounceFn(async (id, body) => {
    if (id) {
      await updateWorkflowApi(workflowId, body)
    }
  }, 500)

  useEffect(() => {
    if (!workflowId || !process.env.NEXT_PUBLIC_Y_WEBSOCKET_URL) {
      return
    }
    const ydoc = new Y.Doc()
    const wsProvider = new WebsocketProvider(
      process.env.NEXT_PUBLIC_Y_WEBSOCKET_URL,
      workflowId,
      ydoc,
    )

    const yWorkflowMap = ydoc.getMap<{
      config: IWorkflowInfo['config']
      nodes: WorkflowNode[]
      edges: WorkflowEdge[]
    }>(workflowId)

    yWorkflowMap.observe((_event, transaction) => {
      if (isInitializing.current) {
        return
      }

      const isLocalChange = transaction.local
      const data = yWorkflowMap.get(workflowId)
      if (data) {
        if (isLocalChange) {
          const oldWorkflowConfig = useWorkflowStore.getState().workflowConfig
          const oldNodes = useWorkflowStore.getState().nodes
          const oldEdges = useWorkflowStore.getState().edges
          const configChanges = calculateWorkflowConfigChanges(data.config, oldWorkflowConfig)
          const nodesChanges = calculateNodesChanges(data.nodes, oldNodes)
          const edgesChanges = calculateEdgesChanges(data.edges, oldEdges)
          if (configChanges || nodesChanges || edgesChanges) {
            saveWorkflowConfig(workflowId, {
              ...nodesChanges,
              ...edgesChanges,
              config: configChanges,
            })
          }
        }

        useWorkflowStore.setState({
          workflowConfig: data.config,
          nodes: data.nodes,
          edges: data.edges,
        })
      }
    })

    const { setYjsState } = useWorkflowStore.getState()
    setYjsState({ ydoc, wsProvider, yWorkflowMap })

    wsProvider.once('sync', () => {
      const { workflow, workflowConfig, nodes, edges } = useWorkflowStore.getState()
      if (workflow) {
        ydoc.transact(() => {
          yWorkflowMap.set(workflow.id, {
            config: workflowConfig || {},
            nodes: nodes || [],
            edges: edges || [],
          })
        }, null)
      }
      isInitializing.current = false
    })

    return () => {
      wsProvider.disconnect()
      ydoc.destroy()
      setYjsState({ ydoc: null, wsProvider: null, yWorkflowMap: null })
    }
  }, [workflowId, saveWorkflowConfig])

  return children
}

function calculateWorkflowConfigChanges(newConfig: IWorkflowInfo['config'], oldConfig: IWorkflowInfo['config']) {
  if (_.isEqual(newConfig, oldConfig)) {
    return null
  }

  return {
    config: newConfig,
  }
}

function calculateNodesChanges(newNodes: WorkflowNode[], oldNodes: WorkflowNode[]) {
  // Convert all nodes to normalized format first
  const normalizedNewNodes = newNodes.map(node => ({
    id: node.data?.id,
    normalized: normalizeWorkflowNode(node),
  }))
  const normalizedOldNodes = oldNodes.map(node => ({
    id: node.data?.id,
    normalized: normalizeWorkflowNode(node),
  }))

  // Return null if normalized nodes are identical
  if (_.isEqual(
    normalizedNewNodes.map(n => n.normalized),
    normalizedOldNodes.map(n => n.normalized),
  )) {
    return null
  }

  return {
    // Create: nodes without id
    create_nodes: normalizedNewNodes
      .filter(node => !node.id)
      .map(node => node.normalized),

    // Update: nodes with id and changed content
    update_nodes: normalizedNewNodes
      .filter((node) => {
        if (!node.id)
          return false
        const oldNode = normalizedOldNodes.find(n => n.id === node.id)
        return oldNode && !_.isEqual(node.normalized, oldNode.normalized)
      })
      .map(node => node.normalized),

    // Delete: ids present in old array but missing in new array
    delete_nodes: _.difference(
      normalizedOldNodes.map(node => node.id).filter(Boolean),
      normalizedNewNodes.map(node => node.id).filter(Boolean),
    ) as string[],
  }
}

function calculateEdgesChanges(newEdges: WorkflowEdge[], oldEdges: WorkflowEdge[]) {
  // Convert all edges to normalized format first
  const normalizedNewEdges = newEdges.map(edge => ({
    id: edge.data?.id,
    normalized: normalizeWorkflowEdge(edge),
  }))
  const normalizedOldEdges = oldEdges.map(edge => ({
    id: edge.data?.id,
    normalized: normalizeWorkflowEdge(edge),
  }))

  // Return null if normalized edges are identical
  if (_.isEqual(
    normalizedNewEdges.map(e => e.normalized),
    normalizedOldEdges.map(e => e.normalized),
  )) {
    return null
  }

  return {
    // Create: edges without id
    create_edges: normalizedNewEdges
      .filter(edge => !edge.id)
      .map(edge => edge.normalized),

    // Update: edges with id and changed content
    update_edges: normalizedNewEdges
      .filter((edge) => {
        if (!edge.id)
          return false
        const oldEdge = normalizedOldEdges.find(e => e.id === edge.id)
        return oldEdge && !_.isEqual(edge.normalized, oldEdge.normalized)
      })
      .map(edge => edge.normalized),

    // Delete: ids present in old array but missing in new array
    delete_edges: _.difference(
      normalizedOldEdges.map(edge => edge.id).filter(Boolean),
      normalizedNewEdges.map(edge => edge.id).filter(Boolean),
    ) as string[],
  }
}
