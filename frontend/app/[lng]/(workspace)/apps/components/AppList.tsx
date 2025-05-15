'use client'

import type { IAppInfo } from '@/apis'
import { Pagination } from '@/components/Pagination'
import AppCard from './AppCard'

interface AppListProps {
  apps: IAppInfo[]
  total: number
  page: number
  pageSize: number
  onPageChange: (page: number, pageSize: number) => void
}

export function AppList({ apps, total, page, pageSize, onPageChange }: AppListProps) {
  return (
    <div className="flex flex-col gap-8 flex-1 overflow-hidden">
      <div className="grid grid-cols-1 content-start sm:grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 2k:grid-cols-5 gap-4 overflow-y-auto p-1 tran">
        {apps.map(app => (
          <AppCard info={app} key={app.id} />
        ))}
      </div>
      <Pagination
        page={page}
        pageSize={pageSize}
        total={total}
        hidePrevText
        hideNextText
        onChange={onPageChange}
        className="w-full px-1"
      />
    </div>
  )
}
