import type { WebsocketProvider } from 'y-websocket'
import type * as Y from 'yjs'
import type { WorkflowEdge, WorkflowNode } from '../types'
import {
  getOperatorsApi,
  getWorkflowApi,
  getWorkflowDebugSnapshotsApi,
  getWorkflowEdgesApi,
  getWorkflowNodesApi,
  getWorkflowVersionsApi,
  type ICreateWorkflowVersionPayload,
  type IOperatorEntity,
  type IWorkflowDebugSnapshotInfo,
  type IWorkflowInfo,
  type IWorkflowVersionInfo,
  publishWorkflowApi,
} from '@/apis'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { addEdge, applyEdgeChanges, applyNodeChanges, type Connection, type EdgeChange, type NodeChange } from '@xyflow/react'
import * as _ from 'lodash-es'
import { create } from 'zustand'
import { convertToReactFlowEdge, convertToReactFlowNode } from '../utils/workflow'

interface WorkflowStoreState {
  workflow: IWorkflowInfo | null
  workflowConfig: IWorkflowInfo['config']
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  operators: IOperatorEntity[]
  versions: IWorkflowVersionInfo[]
  debugSnapshots: IWorkflowDebugSnapshotInfo[]
  ydoc: Y.Doc | null
  wsProvider: WebsocketProvider | null
  yWorkflowMap: Y.Map<{
    config: IWorkflowInfo['config']
    nodes: WorkflowNode[]
    edges: WorkflowEdge[]
  }> | null
  setWorkflow: (workflow: IWorkflowInfo | null) => void
  setNodes: (nodes: WorkflowNode[]) => void
  setEdges: (edges: WorkflowEdge[]) => void
  setWorkflowConfig: (config: IWorkflowInfo['config']) => void
  setOperators: (operators: IOperatorEntity[]) => void
  setVersions: (versions: IWorkflowVersionInfo[]) => void
  setDebugSnapshots: (snapshots: IWorkflowDebugSnapshotInfo[]) => void
  getOperatorInfoByType: (type: IOperatorEntity['name']) => IOperatorEntity | undefined
  onNodesChange: (changes: NodeChange[]) => void
  onEdgesChange: (changes: EdgeChange[]) => void
  onConnect: (connection: Connection) => void
  setYjsState: (state: { ydoc: Y.Doc | null, wsProvider: WebsocketProvider | null, yWorkflowMap: Y.Map<any> | null }) => void
}

export const useWorkflowStore = create<WorkflowStoreState>((set, get) => ({
  workflow: null,
  workflowConfig: null,
  nodes: [],
  edges: [],
  operators: [],
  versions: [],
  debugSnapshots: [],
  ydoc: null,
  wsProvider: null,
  yWorkflowMap: null,
  setWorkflow: (workflow) => {
    set({ workflow })
  },
  setWorkflowConfig: (config) => {
    set({ workflowConfig: config })
  },
  setNodes: (nodes) => {
    set({ nodes })
  },
  setEdges: (edges) => {
    set({ edges })
  },
  setOperators: operators => set({ operators }),
  setVersions: versions => set({ versions }),
  setDebugSnapshots: snapshots => set({ debugSnapshots: snapshots }),
  getOperatorInfoByType: (type: IOperatorEntity['name']) => {
    return get().operators.find(operator => operator.name === type)
  },
  onNodesChange: (changes) => {
    const { nodes } = get()
    const newNodes = applyNodeChanges(changes, nodes) as WorkflowNode[]
    const { yWorkflowMap, workflow } = get()
    if (yWorkflowMap && workflow) {
      const data = yWorkflowMap.get(workflow.id) || { config: {}, nodes: [], edges: [] }
      yWorkflowMap.set(workflow.id, { ...data, nodes: newNodes })
    }
  },
  onEdgesChange: (changes) => {
    const { edges } = get()
    const newEdges = applyEdgeChanges(changes, edges)
    const { yWorkflowMap, workflow } = get()
    if (yWorkflowMap && workflow) {
      const data = yWorkflowMap.get(workflow.id) || { config: {}, nodes: [], edges: [] }
      yWorkflowMap.set(workflow.id, { ...data, edges: newEdges })
    }
  },
  onConnect: (connection) => {
    const { edges } = get()
    const newEdges = addEdge(connection, edges)
    const { yWorkflowMap, workflow } = get()
    if (yWorkflowMap && workflow) {
      const data = yWorkflowMap.get(workflow.id) || { config: {}, nodes: [], edges: [] }
      yWorkflowMap.set(workflow.id, { ...data, edges: newEdges })
    }
  },
  setYjsState: (state: { ydoc: Y.Doc | null, wsProvider: WebsocketProvider | null, yWorkflowMap: Y.Map<any> | null }) => {
    set(state)
  },
}))

export function useWorkflowQuery(workflowId: string) {
  const { setWorkflow, setWorkflowConfig } = useWorkflowStore()

  return useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: async () => {
      const response = await getWorkflowApi(workflowId)
      const workflow = response.data ?? null

      if (workflow) {
        setWorkflow(workflow)
        setWorkflowConfig(workflow.config)
      }

      return workflow
    },
    enabled: !!workflowId,
  })
}

export function useWorkflowNodesQuery(workflowId: string) {
  const { setNodes } = useWorkflowStore()

  return useQuery({
    queryKey: ['workflow-nodes', workflowId],
    queryFn: async () => {
      const response = await getWorkflowNodesApi(workflowId)
      const nodes = response.data ?? []
      setNodes(nodes.map(convertToReactFlowNode))
      return nodes
    },
    enabled: !!workflowId,
  })
}

export function useWorkflowEdgesQuery(workflowId: string) {
  const { setEdges } = useWorkflowStore()

  return useQuery({
    queryKey: ['workflow-edges', workflowId],
    queryFn: async () => {
      const response = await getWorkflowEdgesApi(workflowId)
      const edges = response.data ?? []
      setEdges(edges.map(convertToReactFlowEdge))
      return edges
    },
    enabled: !!workflowId,
  })
}

export function useWorkflowVersionsQuery(workflowId: string) {
  const { setVersions } = useWorkflowStore()

  return useQuery({
    queryKey: ['workflow-versions', workflowId],
    queryFn: async () => {
      const response = await getWorkflowVersionsApi(workflowId)
      const versions = response.data?.versions ?? []
      setVersions(versions)
      return versions
    },
    enabled: !!workflowId,
  })
}

export function useWorkflowDebugSnapshotsQuery(workflowId: string) {
  const { setDebugSnapshots } = useWorkflowStore()

  return useQuery({
    queryKey: ['workflow-debug-snapshots', workflowId],
    queryFn: async () => {
      const response = await getWorkflowDebugSnapshotsApi(workflowId)
      const snapshots = response.data?.snapshots ?? []
      setDebugSnapshots(snapshots)
      return snapshots
    },
    enabled: !!workflowId,
  })
}

export function usePublishWorkflowMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ workflowId, data }: { workflowId: string, data: ICreateWorkflowVersionPayload }) => {
      const response = await publishWorkflowApi(workflowId, data)
      return response.data
    },
    onSuccess: (_, { workflowId }) => {
      queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] })
      queryClient.invalidateQueries({ queryKey: ['workflow-versions', workflowId] })
    },
  })
}

export function useOperatorsQuery() {
  const { setOperators } = useWorkflowStore()

  return useQuery({
    queryKey: ['operators'],
    queryFn: async () => {
      const response = await getOperatorsApi()
      const operators = response.data ?? []
      setOperators(operators)
      return operators
    },
  })
}
