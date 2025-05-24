'use client'

import { useAppStore } from '@/app/[lng]/(workspace)/apps/stores/use-app-store'
import WorkflowEditor from './components/WorkflowEditor'
import WorkflowHeader from './components/WorkflowHeader'
import WorkflowProvider from './components/WorkflowProvider'

export default function Workflow() {
  const { app } = useAppStore()

  if (!app || !app.workflow_id) {
    return null
  }

  return (
    <WorkflowProvider workflowId={app.workflow_id}>
      <div className="relative size-full">
        <WorkflowHeader className="absolute left-0 top-0 z-50" />
        <WorkflowEditor />
      </div>
    </WorkflowProvider>
  )
}
