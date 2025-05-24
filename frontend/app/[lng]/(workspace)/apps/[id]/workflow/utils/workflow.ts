import type {
  ICreateWorkflowEdgePayload,
  ICreateWorkflowNodePayload,
  IUpdateWorkflowEdgePayload,
  IUpdateWorkflowNodePayload,
  IWorkflowEdgeInfo,
  IWorkflowNodeInfo,
} from '@/apis'

import type { WorkflowEdge, WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import * as _ from 'lodash-es'

export function convertToReactFlowNode(node: IWorkflowNodeInfo): WorkflowNode {
  return {
    id: node.node_key,
    type: node.node_type,
    position: node.meta?.position || { x: 0, y: 0 },
    data: {
      ..._.omit(node, ['meta', 'node_type', 'node_key']),
      ..._.omit(node.meta, ['position']),
      operator: node.node_type,
    },
  }
}

export function convertToReactFlowEdge(edge: IWorkflowEdgeInfo): WorkflowEdge {
  return {
    id: edge.edge_key,
    source: edge.source_node_key,
    target: edge.target_node_key,
    data: {
      ..._.omit(edge, ['meta', 'edge_key', 'source_node_key', 'target_node_key']),
    },
  }
}

export function normalizeWorkflowNode(node: WorkflowNode): ICreateWorkflowNodePayload {
  return {
    node_key: node.id,
    node_type: node.type,
    name: node.data.name,
    description: node.data.description,
    config: node.data.config,
    extended_config: node.data.extended_config,
    meta: {
      position: node.position,
      ..._.omit(node.data, ['id', 'name', 'description', 'config', 'extended_config', 'operator']),
    },
  } as unknown as ICreateWorkflowNodePayload
}

export function normalizeWorkflowEdge(edge: WorkflowEdge): ICreateWorkflowEdgePayload {
  return {
    edge_key: edge.id,
    source_node_key: edge.source,
    target_node_key: edge.target,
    meta: {
      ..._.omit(edge.data, ['id']),
    },
  }
}

export function convertToCreateWorkflowNode(node: WorkflowNode): ICreateWorkflowNodePayload {
  return normalizeWorkflowNode(node)
}

export function convertToUpdateWorkflowNode(node: WorkflowNode): IUpdateWorkflowNodePayload {
  return normalizeWorkflowNode(node)
}

export function convertToCreateWorkflowEdge(edge: WorkflowEdge): ICreateWorkflowEdgePayload {
  return normalizeWorkflowEdge(edge)
}

export function convertToUpdateWorkflowEdge(edge: WorkflowEdge): IUpdateWorkflowEdgePayload {
  return normalizeWorkflowEdge(edge)
}
