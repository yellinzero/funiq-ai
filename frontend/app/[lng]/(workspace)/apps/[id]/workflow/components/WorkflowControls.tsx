'use client'

import type { IOperatorEntity } from '@/apis'
import { Button } from '@/components/base/button'
import { MiniMap, Panel, useReactFlow, useViewport } from '@xyflow/react'
import {
  LayoutGrid,
  Map,
  Maximize,
  Minus,
  Plus,
  Redo2,
  Undo2,
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useDagreLayout } from '../hooks/use-dagre-layout'
import { useFlowHandler } from '../hooks/use-flow-handler'
import { useWorkflowStore } from '../stores/use-workflow-store'
import OperatorMenu from './OperatorMenu'

export default function WorkflowControls() {
  const { t } = useTranslation(['app'])
  const { zoomIn, zoomOut, fitView } = useReactFlow()
  const { zoom } = useViewport()
  const [showMiniMap, setShowMiniMap] = useState(false)
  const { layout } = useDagreLayout()
  const { yUndoManager } = useWorkflowStore()
  const { createNode } = useFlowHandler()

  // Track undo/redo state
  const [canUndo, setCanUndo] = useState(false)
  const [canRedo, setCanRedo] = useState(false)
  const [operatorMenuOpen, setOperatorMenuOpen] = useState(false)

  useEffect(() => {
    if (!yUndoManager)
      return

    const updateUndoRedoState = () => {
      setCanUndo(yUndoManager.canUndo())
      setCanRedo(yUndoManager.canRedo())
    }

    updateUndoRedoState()

    yUndoManager.on('stack-item-added', updateUndoRedoState)
    yUndoManager.on('stack-item-popped', updateUndoRedoState)

    return () => {
      yUndoManager.off('stack-item-added', updateUndoRedoState)
      yUndoManager.off('stack-item-popped', updateUndoRedoState)
    }
  }, [yUndoManager])

  const handleZoomIn = useCallback(() => {
    zoomIn()
  }, [zoomIn])

  const handleZoomOut = useCallback(() => {
    zoomOut()
  }, [zoomOut])

  const handleFitView = useCallback(() => {
    fitView()
  }, [fitView])

  const toggleMiniMap = useCallback(() => {
    setShowMiniMap(prev => !prev)
  }, [])

  const handleUndo = useCallback(() => {
    yUndoManager?.undo()
  }, [yUndoManager])

  const handleRedo = useCallback(() => {
    yUndoManager?.redo()
  }, [yUndoManager])

  const handleOperatorSelect = useCallback((operator: IOperatorEntity) => {
    createNode(operator)
  }, [createNode])

  return (
    <Panel position="bottom-left" className="relative flex flex-col gap-2 z-50">
      {showMiniMap && (
        <MiniMap
          style={{
            width: 180,
            height: 140,
          }}
          className="absolute top-[-160px] -left-4 w-[180px] h-[140px]"
        />
      )}

      {/* Controls */}
      <div className="flex items-center gap-1 bg-background p-1 rounded-lg shadow">
        {/* Zoom percentage display */}
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className={showMiniMap ? 'bg-accent text-accent-foreground dark:bg-accent/50' : undefined}
            onClick={toggleMiniMap}
          >
            <Map />
          </Button>
          <Button variant="ghost" size="icon" onClick={handleZoomIn} disabled={zoom >= 2}>
            <Plus />
          </Button>
          <span className="text-center text-sm select-none min-w-10">
            {Math.round(zoom * 100)}
            %
          </span>
          <Button variant="ghost" size="icon" onClick={handleZoomOut} disabled={zoom <= 0.5}>
            <Minus />
          </Button>
        </div>

        {/* other controls */}
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={handleUndo} disabled={!canUndo}>
            <Undo2 />
          </Button>
          <Button variant="ghost" size="icon" onClick={handleRedo} disabled={!canRedo}>
            <Redo2 />
          </Button>
          <Button variant="ghost" size="icon" onClick={handleFitView}>
            <Maximize />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => layout()}
          >
            <LayoutGrid />
          </Button>

          <OperatorMenu
            onSelect={handleOperatorSelect}
            open={operatorMenuOpen}
            onOpenChange={setOperatorMenuOpen}
          >
            <Button size="sm">
              <Plus />
              <span>{t('app.add_node')}</span>
            </Button>
          </OperatorMenu>
        </div>
      </div>
    </Panel>
  )
}
