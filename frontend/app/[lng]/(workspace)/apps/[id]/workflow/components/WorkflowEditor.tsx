'use client'

import type { WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import { useFlowHandler } from '@/app/[lng]/(workspace)/apps/[id]/workflow/hooks/use-flow-handler'
import { useWorkflowStore } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import { Background, BackgroundVariant, ReactFlow } from '@xyflow/react'
import { useState } from 'react'
import { useAwareness } from './AwarenessProvider'
import { NodeEditorDialog } from './NodeEditor/NodeEditorDialog'
import EndNode from './nodes/EndNode'
import LLMNode from './nodes/LLMNode'
import StartNode from './nodes/StartNode'
import WorkflowControls from './WorkflowControls'
import '@xyflow/react/dist/style.css'

const nodeTypes = {
  start: StartNode,
  llm: LLMNode,
  end: EndNode,
}

export default function WorkflowEditor() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
  } = useWorkflowStore()

  const { handleNodesSelect } = useAwareness()
  const { isValidConnection } = useFlowHandler()
  const [editingNode, setEditingNode] = useState<WorkflowNode | null>(null)
  const [isEditorOpen, setIsEditorOpen] = useState(false)

  const onSelectionChange = ({ nodes: selectedNodes }: { nodes: WorkflowNode[] }) => {
    handleNodesSelect(selectedNodes.map(node => node.id))
  }

  const onNodeClick = (_event: React.MouseEvent, node: WorkflowNode) => {
    setEditingNode(node)
    setIsEditorOpen(true)
  }

  return (
    <div className="size-full relative px-2">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onSelectionChange={onSelectionChange}
        onNodeClick={onNodeClick}
        isValidConnection={isValidConnection}
        className="[&_.react-flow\_\_attribution]:select-none"
      >
        <WorkflowControls />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>

      <NodeEditorDialog
        node={editingNode}
        open={isEditorOpen}
        onOpenChange={setIsEditorOpen}
      />
    </div>
  )
}
