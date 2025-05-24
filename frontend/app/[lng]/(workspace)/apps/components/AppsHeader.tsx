'use client'

import { useCreateAppMutation } from '@/app/[lng]/(workspace)/apps/stores/use-apps-store'
import { Button } from '@/components/base/button'
import { Input } from '@/components/base/input'
import { useTranslation } from '@/plugins/i18n/client'
import { Plus, Search } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { AppEditDialog } from './AppEditDialog'

interface AppsHeaderProps {
  searchValue: string
  onSearchChange: (value: string) => void
}

export function AppsHeader({ searchValue, onSearchChange }: AppsHeaderProps) {
  const { t } = useTranslation(['app', 'global'])
  const [isOpen, setIsOpen] = useState(false)
  const createApp = useCreateAppMutation()

  return (
    <div className="flex items-center justify-between gap-4 p-1">
      <div className="relative flex-1 max-w-sm">
        <Search className="absolute left-2 top-2.5 size-4 text-muted-foreground" />
        <Input
          value={searchValue}
          placeholder={t('app.text.search_app')}
          className="pl-8"
          onChange={e => onSearchChange(e.target.value)}
        />
      </div>
      <AppEditDialog
        isOpen={isOpen}
        onOpenChange={setIsOpen}
        mode="create"
        trigger={(
          <Button>
            <Plus className="size-4" />
            {t('app.create_app')}
          </Button>
        )}
        onSubmit={async (data) => {
          await createApp.mutateAsync(data)
          toast.success(t('global.text.create_successfully'))
        }}
      />
    </div>
  )
}
