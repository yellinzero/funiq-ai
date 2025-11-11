'use client'

import type { WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import { Button } from '@/components/base/button'
import { DialogHeader, DialogTitle } from '@/components/base/dialog'
import { Input } from '@/components/base/input'
import { useTranslation } from '@/plugins/i18n/client'
import { Edit3 } from 'lucide-react'
import { useCallback, useRef, useState } from 'react'
import NodeIcon from '../../NodeIcon'

interface NodeEditorDialogHeaderProps {
  node: WorkflowNode | null
  onNameConfirmed: (name: string) => void
}
export function NodeEditorDialogHeader({ node, onNameConfirmed }: NodeEditorDialogHeaderProps) {
  const { t } = useTranslation(['app'])

  const [isEditingName, setIsEditingName] = useState(false)
  const [tempName, setTempName] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const startEditingName = () => {
    setIsEditingName(true)
    setTempName(node?.data.name || '')
  }

  const saveNodeName = useCallback(() => {
    if (!node || tempName.trim() === '')
      return

    onNameConfirmed(tempName.trim())
    setIsEditingName(false)
  }, [node, tempName, onNameConfirmed])

  const cancelEditingName = useCallback(() => {
    setTempName(node?.data.name || '')
    setIsEditingName(false)
  }, [node?.data.name])

  // Handle keyboard events during editing
  const handleNameKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.nativeEvent.isComposing) {
      e.preventDefault()
      saveNodeName()
    }
    else if (e.key === 'Escape') {
      e.preventDefault()
      cancelEditingName()
    }
  }, [saveNodeName, cancelEditingName])

  if (!node)
    return null

  return (
    <DialogHeader className="px-6 py-4 border-b h-[4rem]">
      <div className="flex items-center gap-3 w-[90%] h-full">
        <NodeIcon label={node.data.operator} />
        <div className="flex flex-1 items-center gap-2 group">
          {isEditingName
            ? (
                <Input
                  ref={inputRef}
                  value={tempName}
                  onChange={e => setTempName(e.target.value)}
                  onBlur={saveNodeName}
                  onKeyDown={handleNameKeyDown}
                  placeholder={t('app.node_name')}
                />
              )
            : (
                <div className="flex items-center gap-2">
                  <DialogTitle className="text-lg">{node.data.name}</DialogTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={startEditingName}
                    title={t('app.edit_node_name')}
                  >
                    <Edit3 size={12} />
                  </Button>
                </div>
              )}
        </div>
      </div>
    </DialogHeader>
  )
}
