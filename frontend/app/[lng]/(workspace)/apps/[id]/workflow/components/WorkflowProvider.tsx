import { useOperatorsQuery, useWorkflowEdgesQuery, useWorkflowNodesQuery, useWorkflowQuery } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import FullPageLoading from '@/components/FullPageLoading'
import { useTranslation } from '@/plugins/i18n/client'
import { ReactFlowProvider } from '@xyflow/react'
import { AwarenessProvider } from './AwarenessProvider'
import { YjsProvider } from './YjsProvider'

export default function WorkflowProvider({
  children,
  workflowId,
}: {
  children: React.ReactNode
  workflowId: string
}) {
  const { i18n } = useTranslation()
  const { isLoading } = useWorkflowQuery(workflowId)
  const { isLoading: isNodesLoading } = useWorkflowNodesQuery(workflowId)
  const { isLoading: isEdgesLoading } = useWorkflowEdgesQuery(workflowId)
  useOperatorsQuery(i18n.language)

  if (isLoading || isNodesLoading || isEdgesLoading) {
    return <FullPageLoading />
  }

  return (
    <ReactFlowProvider>
      <YjsProvider workflowId={workflowId}>
        <AwarenessProvider>
          {children}
        </AwarenessProvider>
      </YjsProvider>
    </ReactFlowProvider>
  )
}
