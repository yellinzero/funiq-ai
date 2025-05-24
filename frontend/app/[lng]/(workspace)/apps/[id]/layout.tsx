'use client'

import { useAppQuery } from '@/app/[lng]/(workspace)/apps/stores/use-app-store'
import FullPageLoading from '@/components/FullPageLoading'
import { useParams } from 'next/navigation'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { id } = useParams()
  const { isLoading } = useAppQuery(id as string)
  if (isLoading)
    return <FullPageLoading />
  return children
}
