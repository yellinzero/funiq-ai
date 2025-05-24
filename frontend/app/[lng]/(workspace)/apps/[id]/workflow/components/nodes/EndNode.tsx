'use client'

import type { BaseWorkflowNodeProps } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import BaseNode from './BaseNode'

export default function EndNode(props: BaseWorkflowNodeProps) {
  return <BaseNode {...props} icon={<div className="bg-blue-500 rounded size-5 text-white flex items-center justify-center">E</div>} />
}
