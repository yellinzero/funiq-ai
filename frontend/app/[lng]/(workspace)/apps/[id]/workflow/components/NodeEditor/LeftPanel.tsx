'use client'

import type { WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/base/select'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import { getIncomers, useReactFlow } from '@xyflow/react'
import dynamic from 'next/dynamic'
import { useEffect, useMemo, useState } from 'react'
import NodeIcon from '../NodeIcon'

const InputPanel = dynamic(() => import('./components/InputPanel').then(mod => ({ default: mod.InputPanel })), {
  ssr: false,
})

interface LeftPanelProps {
  isOpen: boolean
  currentNode?: WorkflowNode | null
  className?: string
}

export function LeftPanel({ isOpen, currentNode, className }: LeftPanelProps) {
  const { getNode, getNodes, getEdges } = useReactFlow()
  const { t } = useTranslation(['app'])

  // Get all upstream nodes using React Flow's built-in function
  const upstreamNodes = useMemo(() => {
    if (!currentNode)
      return []

    const node = getNode(currentNode.id)
    if (!node)
      return []

    return getIncomers(node, getNodes(), getEdges()) as WorkflowNode[]
  }, [currentNode, getNode, getNodes, getEdges])

  // State for the currently selected upstream node
  const [selectedUpstreamNodeId, setSelectedUpstreamNodeId] = useState<string>('')

  // Auto-select the first upstream node when the list changes
  useEffect(() => {
    if (upstreamNodes.length > 0) {
      const firstNodeId = upstreamNodes[0]?.id
      if (firstNodeId && firstNodeId !== selectedUpstreamNodeId && (!selectedUpstreamNodeId || !upstreamNodes.find(n => n.id === selectedUpstreamNodeId))) {
        setSelectedUpstreamNodeId(firstNodeId)
      }
    }
    else {
      setSelectedUpstreamNodeId('')
    }
  }, [upstreamNodes, selectedUpstreamNodeId])

  // Get the currently selected upstream node
  const selectedUpstreamNode = useMemo(() => {
    return upstreamNodes.find(n => n.id === selectedUpstreamNodeId) || null
  }, [upstreamNodes, selectedUpstreamNodeId])

  return (
    <div className={cn('flex flex-col h-full overflow-hidden', className)}>
      {/* Left panel header */}
      <div className="px-3 py-3 border-b bg-muted/30 flex items-center justify-between">
        <h3 className="font-medium text-sm flex-1">{t('app.input')}</h3>
      </div>

      {/* Left panel content */}
      {isOpen && (
        <div className="flex flex-col flex-1">
          {/* Upstream node selector */}
          {upstreamNodes.length > 1 && (
            <div className="p-3 border-b bg-gray-50/50">
              <label className="text-xs font-medium text-gray-600 mb-2 block">{t('app.upstream_nodes')}</label>
              <Select value={selectedUpstreamNodeId} onValueChange={setSelectedUpstreamNodeId}>
                <SelectTrigger className="h-8 text-sm">
                  <SelectValue placeholder={t('app.tip.select_upstream_node')}>
                    {selectedUpstreamNode && (
                      <div className="flex items-center gap-2">
                        <NodeIcon label={selectedUpstreamNode.data.operator} />
                        <span className="truncate">{selectedUpstreamNode.data.name}</span>
                      </div>
                    )}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {upstreamNodes.map(node => (
                    <SelectItem key={node.id} value={node.id}>
                      <div className="flex items-center gap-2">
                        <NodeIcon label={node.data.operator} />
                        <span>{node.data.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Input panel */}
          <InputPanel
            upstreamNodeName={selectedUpstreamNode?.data.name}
            inputData={selectedUpstreamNode?.data.output}
          />
        </div>
      )}
    </div>
  )
}
