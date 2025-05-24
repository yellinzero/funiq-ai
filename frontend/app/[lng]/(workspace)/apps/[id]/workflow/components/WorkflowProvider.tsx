import { useOperatorsQuery, useWorkflowEdgesQuery, useWorkflowNodesQuery, useWorkflowQuery } from '@/app/[lng]/(workspace)/apps/[id]/workflow/stores/use-workflow-store'
import FullPageLoading from '@/components/FullPageLoading'
import { AwarenessProvider } from './AwarenessProvider'
import { YjsProvider } from './YjsProvider'

export default function WorkflowProvider({
  children,
  workflowId,
}: {
  children: React.ReactNode
  workflowId: string
}) {
  const { isLoading } = useWorkflowQuery(workflowId)
  const { isLoading: isNodesLoading } = useWorkflowNodesQuery(workflowId)
  const { isLoading: isEdgesLoading } = useWorkflowEdgesQuery(workflowId)
  useOperatorsQuery()

  if (isLoading || isNodesLoading || isEdgesLoading) {
    return <FullPageLoading />
  }

  return (
    <YjsProvider workflowId={workflowId}>
      <AwarenessProvider>
        {children}
      </AwarenessProvider>
    </YjsProvider>
  )
}
