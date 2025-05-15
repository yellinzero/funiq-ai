'use client'

import {
  Pagination as BasePagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/base/pagination'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/base/select'
import { cn } from '@/utils/ui'
import { useTranslation } from 'react-i18next'
import { Input } from './base/input'

type PaginationSize = 'small' | 'default' | 'large'
type PaginationLayout = 'sizes' | 'prev' | 'pager' | 'next' | 'jumper' | 'total'
interface PaginationProps {
  page: number
  pageSize: number
  total: number
  pageSizeOptions?: number[]
  onChange?: (page: number, pageSize: number) => void
  className?: string
  size?: PaginationSize
  background?: boolean
  disabled?: boolean
  hideOnSinglePage?: boolean
  layout?: PaginationLayout[]
  hidePrevText?: boolean
  hideNextText?: boolean
}

const DEFAULT_PAGE_SIZES = [10, 20, 30, 50]
const DEFAULT_LAYOUT: PaginationLayout[] = ['total', 'prev', 'pager', 'next', 'sizes']

export function Pagination({
  page,
  pageSize,
  total,
  pageSizeOptions = DEFAULT_PAGE_SIZES,
  onChange,
  className,
  size = 'default',
  hidePrevText = false,
  hideNextText = false,
  background = false,
  disabled = false,
  hideOnSinglePage = false,
  layout = DEFAULT_LAYOUT,
}: PaginationProps) {
  const { t } = useTranslation('component')
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const isEmpty = total === 0

  if (hideOnSinglePage && totalPages <= 1 && !isEmpty) {
    return null
  }

  const getPageNumbers = () => {
    if (isEmpty) {
      return [1]
    }

    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    if (page <= 3) {
      return [1, 2, 3, 4, 5, null, totalPages]
    }

    if (page >= totalPages - 2) {
      return [1, null, totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages]
    }

    return [1, null, page - 1, page, page + 1, null, totalPages]
  }

  const handlePageChange = (newPage: number) => {
    if ((!isEmpty && !disabled) && newPage >= 1 && newPage <= totalPages) {
      onChange?.(newPage, pageSize)
    }
  }

  const handlePageSizeChange = (newSize: string) => {
    if (!isEmpty && !disabled) {
      const size = Number.parseInt(newSize, 10)
      const newPage = Math.floor(((page - 1) * pageSize) / size) + 1
      onChange?.(newPage, size)
    }
  }

  const sizeClasses = {
    small: '!text-xs',
    default: '!text-sm',
    large: '!text-base',
  }

  const buttonSizeClasses = {
    small: '!h-7 !px-2',
    default: '!h-9 !px-3',
    large: '!h-11 !px-4',
  }

  const iconButtonSizeClasses = {
    small: '!h-7 !w-7',
    default: '!h-9 !w-9',
    large: '!h-11 !w-11',
  }

  const selectSizeClasses = {
    small: '!px-2 !py-1 !text-xs !h-7 !w-[60px]',
    default: '!px-3 !py-1.5 !text-sm !h-9 !w-[70px]',
    large: '!px-4 !py-2 !text-base !h-11 !w-[80px]',
  }

  const inputSizeClasses = {
    small: '!h-7 !px-2 !w-[60px]',
    default: '!h-9 !px-3 !w-[70px]',
    large: '!h-11 !px-4 !w-[80px]',
  }

  const childSvgSizeClasses = {
    small: '[&_svg]:!size-3',
    default: '[&_svg]:!size-4',
    large: '[&_svg]:!size-5',
  }

  const renderLayout = () => {
    return layout.map((item, index) => {
      switch (item) {
        case 'total':
          return (
            <span key={item} className={cn('text-muted-foreground shrink-0', sizeClasses[size])}>
              {t('component.pagination.total', { count: total })}
            </span>
          )
        case 'sizes':
          return (
            <div key={item} className="flex items-center gap-2">
              <span className={cn('text-muted-foreground shrink-0', sizeClasses[size])}>
                {t('component.pagination.page_size')}
              </span>
              <Select
                value={pageSize.toString()}
                onValueChange={handlePageSizeChange}
                disabled={disabled || isEmpty}
              >
                <SelectTrigger className={cn(
                  selectSizeClasses[size],
                  childSvgSizeClasses[size],
                )}
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {pageSizeOptions.map(pageSize => (
                    <SelectItem
                      key={pageSize}
                      value={pageSize.toString()}
                      className={sizeClasses[size]}
                    >
                      {pageSize}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )
        case 'prev':
        case 'pager':
        case 'next':
          return index === layout.indexOf('prev')
            ? (
                <BasePagination key="pagination" className="w-auto mx-0">
                  <PaginationContent>
                    <PaginationItem>
                      <PaginationPrevious
                        onClick={() => handlePageChange(page - 1)}
                        hideText={hidePrevText}
                        className={cn(
                          childSvgSizeClasses[size],
                          sizeClasses[size],
                          buttonSizeClasses[size],
                          background && 'bg-background',
                          (page <= 1 || disabled || isEmpty) ? 'pointer-events-none opacity-50' : 'cursor-pointer',
                        )}
                      />
                    </PaginationItem>

                    {getPageNumbers().map(pageNumber => (
                      pageNumber === null
                        ? (
                            <PaginationItem key={`ellipsis-${page <= 3 ? 'start' : 'end'}`}>
                              <PaginationEllipsis className={cn(sizeClasses[size], iconButtonSizeClasses[size])} />
                            </PaginationItem>
                          )
                        : (
                            <PaginationItem key={pageNumber}>
                              <PaginationLink
                                onClick={() => handlePageChange(pageNumber)}
                                isActive={page === pageNumber}
                                className={cn(
                                  sizeClasses[size],
                                  iconButtonSizeClasses[size],
                                  background && 'bg-background',
                                  'cursor-pointer',
                                  (disabled || isEmpty) && 'pointer-events-none opacity-50',
                                )}
                              >
                                {pageNumber}
                              </PaginationLink>
                            </PaginationItem>
                          )
                    ))}

                    <PaginationItem>
                      <PaginationNext
                        onClick={() => handlePageChange(page + 1)}
                        hideText={hideNextText}
                        className={cn(
                          childSvgSizeClasses[size],
                          sizeClasses[size],
                          buttonSizeClasses[size],
                          background && 'bg-background',
                          (page >= totalPages || disabled || isEmpty) ? 'pointer-events-none opacity-50' : 'cursor-pointer',
                        )}
                      />
                    </PaginationItem>
                  </PaginationContent>
                </BasePagination>
              )
            : null
        case 'jumper':
          return (
            <div key={item} className="flex items-center gap-2">
              <span className={cn('text-muted-foreground shrink-0', sizeClasses[size])}>
                {t('component.pagination.jump_to')}
              </span>
              <Input
                type="number"
                className={cn(
                  sizeClasses[size],
                  inputSizeClasses[size],
                )}
                value={page}
                onChange={e => handlePageChange(Number(e.target.value))}
                disabled={disabled || isEmpty}
              />
            </div>
          )
        default:
          return null
      }
    })
  }

  return (
    <div className={cn('flex w-full items-center justify-end gap-4', className)}>
      {renderLayout()}
    </div>
  )
}
