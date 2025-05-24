'use client'

import { useWorkflowStore } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import { useUserById } from '@/app/[lng]/stores/use-global-store'
import { Button } from '@/components/base/button'
import RelativeTime from '@/components/RelativeTime'
import { useTranslation } from '@/plugins/i18n/client'
import { convertTime } from '@/utils/time'
import { cn } from '@/utils/ui'
import { History } from 'lucide-react'

export default function WorkflowHeader({
  className,
}: {
  className?: string
}) {
  const { t } = useTranslation(['app'])
  const { workflow } = useWorkflowStore()
  const user = useUserById(workflow?.updated_by ?? '')

  if (!workflow)
    return null

  const status = workflow.status === 'published' ? t('app.published') : t('app.unpublished')

  return (
    <div className={cn('flex items-center w-full px-4', className)}>
      <div className="flex-1">
        <div className="flex items-center text-xs gap-0.5">
          <span>{user?.name ?? '--'}</span>
          <span className="text-[9px]">•</span>
          <RelativeTime date={convertTime(workflow.updated_at)} />
          <span className="text-[9px]">•</span>
          <span>{status}</span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button size="sm">
          {t('app.publish')}
        </Button>
        <Button variant="outline" size="sm" className="size-8">
          <History className="size-4" />
        </Button>
      </div>
    </div>
  )
}
