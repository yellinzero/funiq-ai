'use client'

import FullPageLoading from '@/components/FullPageLoading'
import { useDebounce } from '@reactuses/core'
import { useEffect, useState } from 'react'
import { AppList } from './components/AppList'
import { AppsHeader } from './components/AppsHeader'
import { useAppsQuery } from './stores/use-apps-store'

export default function Apps() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchValue, setSearchValue] = useState('')
  const debouncedSearchValue = useDebounce(searchValue, 300)
  const { data, isLoading } = useAppsQuery(page, pageSize, debouncedSearchValue)

  useEffect(() => {
    setPage(1)
  }, [debouncedSearchValue])

  const handlePageChange = (newPage: number, newPageSize: number) => {
    setPage(newPage)
    setPageSize(newPageSize)
  }

  return (
    <div className="flex flex-col gap-2 p-3 size-full">
      <AppsHeader
        searchValue={searchValue}
        onSearchChange={setSearchValue}
      />
      {isLoading
        ? (
            <FullPageLoading />
          )
        : (
            <AppList
              apps={data?.apps || []}
              total={data?.total || 0}
              page={page}
              pageSize={pageSize}
              onPageChange={handlePageChange}
            />
          )}
    </div>
  )
}
