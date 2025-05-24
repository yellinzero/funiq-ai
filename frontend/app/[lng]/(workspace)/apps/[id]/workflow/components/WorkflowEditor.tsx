'use client'

import type { WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import { useWorkflowStore } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import { Background, BackgroundVariant, Controls, MiniMap, ReactFlow } from '@xyflow/react'
import { useAwareness } from './AwarenessProvider'
import EndNode from './nodes/EndNode'
import LLMNode from './nodes/LLMNode'
import StartNode from './nodes/StartNode'
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

  const onSelectionChange = ({ nodes: selectedNodes }: { nodes: WorkflowNode[] }) => {
    handleNodesSelect(selectedNodes.map(node => node.id))
  }

  return (
    <div className="size-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onSelectionChange={onSelectionChange}
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>

  )
}
