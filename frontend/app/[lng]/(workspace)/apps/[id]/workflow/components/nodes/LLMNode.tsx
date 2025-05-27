'use client'
import type { BaseWorkflowNodeProps } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import NodeIcon from '@/app/[lng]/(workspace)/apps/[id]/workflow/components/NodeIcon'
import BaseNode from './BaseNode'

export default function LLMNode(props: BaseWorkflowNodeProps) {
  const { type } = props
  return <BaseNode {...props} icon={<NodeIcon label={type} />} />
}
