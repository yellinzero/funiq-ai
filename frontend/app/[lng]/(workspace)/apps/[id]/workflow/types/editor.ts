import type { IOperatorName, IWorkflowEdgeInfo, IWorkflowNodeInfo } from '@/apis'
import type { Edge, Node, NodeProps } from '@xyflow/react'

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
