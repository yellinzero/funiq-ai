import type { WorkflowEdge, WorkflowNode, WorkflowState, WorkflowUpdateState } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
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

  const getYWorkflowMapKey = (id: string) => id
  const getYWorkflowUpdateStateMapKey = (id: string) => `workflow-update-state-${id}`
  const { run: saveWorkflowConfig } = useDebounceFn(async (id, body) => {
    if (id) {
      const res = await updateWorkflowApi(workflowId, body)
      if (res.data) {
        const { setWorkflowUpdated, yWorkflowUpdateStateMap } = useWorkflowStore.getState()
        const key = getYWorkflowUpdateStateMapKey(workflowId)
        if (yWorkflowUpdateStateMap) {
          const data = yWorkflowUpdateStateMap.get(key)
          if (data) {
            setWorkflowUpdated(res.data.updated_at, res.data.updated_by)
            yWorkflowUpdateStateMap.set(key, {
              updated_at: data.updated_at,
              updated_by: data.updated_by,
            })
          }
        }
      }
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
    const workflowMapKey = getYWorkflowMapKey(workflowId)
    const workflowUpdateStateKey = getYWorkflowUpdateStateMapKey(workflowId)

    const yWorkflowMap = ydoc.getMap<WorkflowState>(workflowMapKey)
    const yWorkflowUpdateStateMap = ydoc.getMap<WorkflowUpdateState>(workflowUpdateStateKey)

    yWorkflowMap.observe(async (_event, transaction) => {
      if (isInitializing.current) {
        return
      }
      const { setWorkflowConfig, setNodes, setEdges, workflowConfig: oldWorkflowConfig, nodes: oldNodes, edges: oldEdges } = useWorkflowStore.getState()

      const isLocalChange = transaction.local
      const data = yWorkflowMap.get(workflowMapKey)
      if (data) {
        if (isLocalChange) {
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

        setWorkflowConfig(data.config)
        setNodes(data.nodes)
        setEdges(data.edges)
      }
    })

    yWorkflowUpdateStateMap.observe(() => {
      if (isInitializing.current) {
        return
      }
      const { setWorkflowUpdated } = useWorkflowStore.getState()
      const data = yWorkflowUpdateStateMap.get(workflowUpdateStateKey)
      if (data) {
        setWorkflowUpdated(data.updated_at, data.updated_by)
      }
    })

    const { setYjsState } = useWorkflowStore.getState()
    setYjsState({ ydoc, wsProvider, yWorkflowMap, yWorkflowUpdateStateMap })

    wsProvider.once('sync', () => {
      const { workflow, workflowConfig, nodes, edges } = useWorkflowStore.getState()
      if (workflow) {
        ydoc.transact(() => {
          yWorkflowMap.set(workflow.id, {
            config: workflowConfig,
            nodes: nodes || [],
            edges: edges || [],
          })
          yWorkflowUpdateStateMap.set(workflow.id, {
            updated_at: workflow.updated_at,
            updated_by: workflow.updated_by,
          })
        }, null)
      }
      isInitializing.current = false
      const yUndoManager = new Y.UndoManager(yWorkflowMap)
      setYjsState({ yUndoManager })
    })

    return () => {
      wsProvider.disconnect()
      ydoc.destroy()
      setYjsState({ ydoc: null, wsProvider: null, yUndoManager: null, yWorkflowMap: null, yWorkflowUpdateStateMap: null })
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
  const normalizedNewNodes = newNodes.map(normalizeWorkflowNode)
  const normalizedOldNodes = oldNodes.map(normalizeWorkflowNode)

  if (_.isEqual(
    normalizedNewNodes,
    normalizedOldNodes,
  )) {
    return null
  }

  const oldKeys = new Set(normalizedOldNodes.map(n => n.node_key))
  const newKeys = new Set(normalizedNewNodes.map(n => n.node_key))

  return {
    update_nodes: normalizedNewNodes,
    delete_nodes: Array.from(oldKeys).filter(key => !newKeys.has(key)),
  }
}

function calculateEdgesChanges(newEdges: WorkflowEdge[], oldEdges: WorkflowEdge[]) {
  const normalizedNewEdges = newEdges.map(normalizeWorkflowEdge)
  const normalizedOldEdges = oldEdges.map(normalizeWorkflowEdge)

  // Return null if normalized edges are identical
  if (_.isEqual(
    normalizedNewEdges,
    normalizedOldEdges,
  )) {
    return null
  }

  const oldKeys = new Set(normalizedOldEdges.map(e => e.edge_key))
  const newKeys = new Set(normalizedNewEdges.map(e => e.edge_key))

  return {
    update_edges: normalizedNewEdges,
    delete_edges: Array.from(oldKeys).filter(key => !newKeys.has(key)),
  }
}
