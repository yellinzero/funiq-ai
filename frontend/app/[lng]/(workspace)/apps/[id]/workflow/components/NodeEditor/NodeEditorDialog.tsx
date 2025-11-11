'use client'

import type { WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import { useWorkflowStore } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import { Button } from '@/components/base/button'
import { Dialog, DialogContent } from '@/components/base/dialog'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import { useDebounceFn } from '@reactuses/core'
import { cloneDeep, isEqual } from 'lodash-es'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { CenterPanel } from './CenterPanel'
import { NodeEditorDialogHeader } from './components/NodeEditorDialogHeader'
import { LeftPanel } from './LeftPanel'
import { RightPanel } from './RightPanel'

interface NodeEditorDialogProps {
  node: WorkflowNode | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface NodeEditableBasicData {
  name?: string
  description?: string | null
}

interface NodeEditableConfigData {
  config?: Record<string, any> | null
}

export function NodeEditorDialog({ node, open, onOpenChange }: NodeEditorDialogProps) {
  const { getOperatorInfoByType, yWorkflowMap, workflow } = useWorkflowStore()
  const { t } = useTranslation(['app'])
  const [isLeftPanelOpen, setIsInputPanelOpen] = useState(false)
  const [isRightPanelOpen, setIsOutputPanelOpen] = useState(false)

  // Internal node data, initial value is node, and update when node changes
  const [innerNode, setInnerNode] = useState<WorkflowNode | null>(node)

  // Sync internal node with external node prop changes
  useEffect(() => {
    setInnerNode(node)
  }, [node])

  // Get operator information for the current node
  const operatorInfo = useMemo(() => {
    if (!innerNode)
      return null
    return getOperatorInfoByType(innerNode.data.operator)
  }, [innerNode, getOperatorInfoByType])

  // Update node data to yWorkflowMap and sync internal state
  const updateToYJS = useCallback((updatedNode: WorkflowNode) => {
    if (!workflow || !yWorkflowMap)
      return

    const currentState = yWorkflowMap.get(workflow.id)
    if (!currentState)
      return

    const nodeIndex = currentState.nodes.findIndex(n => n.id === updatedNode.id)
    if (nodeIndex === -1)
      return

    const nodesCopy = cloneDeep(currentState.nodes)
    nodesCopy[nodeIndex] = updatedNode
    yWorkflowMap.set(workflow.id, {
      ...currentState,
      nodes: nodesCopy,
    })

    // Sync internal node state with updated node
    setInnerNode(updatedNode)
  }, [workflow, yWorkflowMap])

  // Update basic node data (name and description)
  const updateBasicData = useCallback((basicData: NodeEditableBasicData) => {
    if (!innerNode)
      return

    const hasChanges = !isEqual(
      { name: innerNode.data.name, description: innerNode.data.description },
      basicData,
    )

    if (!hasChanges)
      return

    const updatedNode = {
      ...innerNode,
      data: {
        ...innerNode.data,
        ...(basicData.name !== undefined && { name: basicData.name.trim() }),
        ...(basicData.description !== undefined && { description: basicData.description?.trim() || '' }),
      },
    }

    updateToYJS(updatedNode)
  }, [innerNode, updateToYJS])

  // Update node configuration data
  const updateConfigData = useCallback(({
    config,
  }: NodeEditableConfigData) => {
    if (!innerNode || !config)
      return

    const hasChanges = !isEqual(
      { config: innerNode.data.config },
      { config },
    )

    if (!hasChanges)
      return

    const updatedNode = {
      ...innerNode,
      data: {
        ...innerNode.data,
        config,
      },
    }

    updateToYJS(updatedNode)
  }, [innerNode, updateToYJS])

  // Debounced versions of update functions
  const { run: updateBasicDataDebounced } = useDebounceFn(updateBasicData, 300)
  const { run: updateConfigDataDebounced } = useDebounceFn(updateConfigData, 300)

  // Handle basic settings changes with debouncing
  const handleNodeBasicSettingChange = useCallback((data: NodeEditableBasicData) => {
    updateBasicDataDebounced(data)
  }, [updateBasicDataDebounced])

  // Handle configuration changes with debouncing
  const handleConfigChange = useCallback((config: NodeEditableConfigData['config']) => {
    updateConfigDataDebounced({
      config,
    })
  }, [updateConfigDataDebounced])

  // Save node name with trimming and validation
  const saveNodeName = useCallback((name: string) => {
    const trimmedName = name.trim()
    if (!innerNode || trimmedName === '')
      return

    updateBasicDataDebounced({ name: trimmedName })
  }, [innerNode, updateBasicDataDebounced])

  // Determine whether to show left/right panels based on node type
  const hasInputPanel = useMemo(() => innerNode?.data.operator !== 'start', [innerNode?.data.operator])
  const hasOutputPanel = useMemo(() => innerNode?.data.operator !== 'end', [innerNode?.data.operator])

  // Track whether both panels are open for responsive layout
  const bothPanelsOpen = useMemo(() => isLeftPanelOpen && isRightPanelOpen, [isLeftPanelOpen, isRightPanelOpen])

  // Memoized left panel toggle button
  const leftButton = useMemo(() => {
    return hasInputPanel && (
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 ml-1"
        onClick={() => setIsInputPanelOpen(!isLeftPanelOpen)}
        title={isLeftPanelOpen ? t('app.collapse') : t('app.expand')}
      >
        {isLeftPanelOpen ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </Button>
    )
  }, [hasInputPanel, isLeftPanelOpen, t])

  // Memoized right panel toggle button
  const rightButton = useMemo(() => {
    return hasOutputPanel && (
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 mr-1"
        onClick={() => setIsOutputPanelOpen(!isRightPanelOpen)}
        title={isRightPanelOpen ? t('app.collapse') : t('app.expand')}
      >
        {isRightPanelOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </Button>
    )
  }, [hasOutputPanel, isRightPanelOpen, t])

  if (!innerNode || !operatorInfo)
    return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={cn('!max-w-[50vw] h-[90vh] p-0 gap-0 flex flex-col', bothPanelsOpen && '!max-w-[35vw]', !bothPanelsOpen && isLeftPanelOpen && 'left-[70vw]', !bothPanelsOpen && isRightPanelOpen && 'left-[30vw]')}>
        <NodeEditorDialogHeader
          node={innerNode}
          onNameConfirmed={saveNodeName}
        />

        <div className="flex relative h-[calc(90vh-4rem)]">
          {/* Input */}
          {hasInputPanel && (
            <div
              className={cn(
                'border-r transition-all duration-300 flex-shrink-0 absolute -top-[40px] bg-background h-full z-10 rounded-l-2xl overflow-hidden',
                isLeftPanelOpen ? 'w-[30vw] -left-[30vw]' : 'w-2 -left-2',
              )}
            >
              <LeftPanel
                isOpen={isLeftPanelOpen}
                currentNode={innerNode}
                className="h-full"
              />
            </div>
          )}

          {/* Parameters */}
          <div className={cn('flex-1 flex flex-col overflow-hidden')}>
            <CenterPanel
              node={innerNode}
              operatorInfo={operatorInfo}
              onNodeBasicSettingChange={handleNodeBasicSettingChange}
              onConfigChange={handleConfigChange}
              leftButton={leftButton}
              rightButton={rightButton}
            />
          </div>

          {/* Output */}
          {hasOutputPanel && (
            <div
              className={cn(
                'border-l transition-all duration-300 flex-shrink-0 absolute -top-[40px] bg-white h-full z-10 rounded-r-2xl overflow-hidden',
                isRightPanelOpen ? 'w-[30vw] -right-[30vw]' : 'w-2 -right-2',
              )}
            >
              <RightPanel
                isOpen={isRightPanelOpen}
                operatorInfo={operatorInfo}
                actualOutput={innerNode.data.output}
                hasExecuted={!!innerNode.data.output}
                className="h-full"
              />
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
