'use client'

import type { IOperatorEntity, IOperatorType } from '@/apis'
import { useWorkflowStore } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import { Button } from '@/components/base/button'
import { Input } from '@/components/base/input'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/base/popover'
import { TruncatedText } from '@/components/TruncatedText'
import { SearchX } from 'lucide-react'
import { useCallback, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import NodeIcon from './NodeIcon'

// 操作符类型的显示名称映射
const OPERATOR_TYPE_LABELS: Record<IOperatorType, string> = {
  task: 'Tasks',
  start: 'Start',
  end: 'End',
  logic: 'Logic',
}

interface OperatorMenuProps {
  children: React.ReactNode
  onSelect?: (operator: IOperatorEntity) => void
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export default function OperatorMenu({
  children,
  onSelect,
  open,
  onOpenChange,
}: OperatorMenuProps) {
  const { operators } = useWorkflowStore()
  const [search, setSearch] = useState('')
  const { t } = useTranslation(['app'])

  // Group operators and filter by search
  const groupedOperators = useMemo(() => {
    const groups = new Map<IOperatorType, IOperatorEntity[]>()

    // Initialize all operator type groups
    Object.keys(OPERATOR_TYPE_LABELS).forEach((type) => {
      groups.set(type as IOperatorType, [])
    })

    // Filter and group operators
    operators.forEach((operator) => {
      if (search && !operator.label.toLowerCase().includes(search.toLowerCase())) {
        return
      }

      const group = groups.get(operator.type) || []
      group.push(operator)
      groups.set(operator.type, group)
    })

    return groups
  }, [operators, search])

  const handleSelect = useCallback((operator: IOperatorEntity) => {
    onSelect?.(operator)
    onOpenChange?.(false)
  }, [onSelect, onOpenChange])

  // 检查是否有任何可见的操作符
  const hasVisibleOperators = useMemo(() => {
    return Array.from(groupedOperators.values()).some(group => group.length > 0)
  }, [groupedOperators])

  return (
    <Popover open={open} onOpenChange={onOpenChange}>
      <PopoverTrigger asChild>
        {children}
      </PopoverTrigger>
      <PopoverContent className="w-[280px] py-2 px-1">
        <div className="space-y-4">
          <div className="px-1">
            <Input
              placeholder={t('app.text.search_operator')}
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="h-8"
            />
          </div>

          {!hasVisibleOperators && (
            <div className="flex flex-col items-center justify-center py-8 text-muted-foreground gap-2">
              <SearchX className="size" />
              <span className="text-sm">{t('app.text.no_operator_found')}</span>
            </div>
          )}

          {hasVisibleOperators && (
            <div className="flex flex-col gap-1">
              {Array.from(groupedOperators.entries()).map(([type, ops]) => (
                ops.length > 0 && (
                  <div key={type} className="flex flex-col gap-1">
                    <div className="text-sm font-medium text-muted-foreground px-3">
                      {OPERATOR_TYPE_LABELS[type]}
                    </div>
                    <div className="flex flex-col gap-1">
                      {ops.map(operator => (
                        <Button
                          key={operator.name}
                          variant="ghost"
                          size="sm"
                          className="w-full justify-start gap-2"
                          onClick={() => handleSelect(operator)}
                        >
                          <NodeIcon label={operator.name} />
                          <TruncatedText className="text-sm" text={operator.label} />
                        </Button>
                      ))}
                    </div>
                  </div>
                )
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}
