import type { IOperatorName, IWorkflowEdgeInfo, IWorkflowInfo, IWorkflowNodeInfo } from '@/apis'
import type { Edge, Node, NodeProps } from '@xyflow/react'
import type { WebsocketProvider } from 'y-websocket'
import type * as Y from 'yjs'

export interface WorkflowNodeData extends Partial<IWorkflowNodeInfo>, Record<string, unknown> {
  id?: string
  operator: IOperatorName
  config?: IWorkflowNodeInfo['config']
  extended_config?: IWorkflowNodeInfo['extended_config']
  name: string
  description?: string | null
}

export interface WorkflowEdgeData extends Partial<IWorkflowEdgeInfo>, Record<string, unknown> {
  id?: string
}

export interface WorkflowNode extends Node {
  data: WorkflowNodeData
}

export interface BaseWorkflowNodeProps extends NodeProps {
  data: WorkflowNodeData
}

export interface WorkflowEdge extends Edge {
  data?: {
    id?: string
  }
}

export interface WorkflowUpdateState {
  updated_at: string
  updated_by: string
}
export interface WorkflowState {
  config: IWorkflowInfo['config']
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

export interface YjsState {
  ydoc?: Y.Doc | null
  wsProvider?: WebsocketProvider | null
  yUndoManager?: Y.UndoManager | null
  yWorkflowMap?: Y.Map<WorkflowState> | null
  yWorkflowUpdateStateMap?: Y.Map<WorkflowUpdateState> | null
}
