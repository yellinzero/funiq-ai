import type {
  ISaveWorkflowEdgePayload,
  ISaveWorkflowNodePayload,
  IWorkflowEdgeInfo,
  IWorkflowNodeInfo,
} from '@/apis'

import type { WorkflowEdge, WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import * as _ from 'lodash-es'

import { customAlphabet } from 'nanoid'

export const nanoid = customAlphabet(
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
  10,
)

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

export function normalizeWorkflowNode(node: WorkflowNode): ISaveWorkflowNodePayload {
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
  } as unknown as ISaveWorkflowNodePayload
}

export function normalizeWorkflowEdge(edge: WorkflowEdge): ISaveWorkflowEdgePayload {
  return {
    edge_key: edge.id,
    source_node_key: edge.source,
    target_node_key: edge.target,
    meta: {
      ..._.omit(edge.data, ['id']),
    },
  }
}
