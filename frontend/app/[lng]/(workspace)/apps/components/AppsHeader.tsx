'use client'

import { useCreateAppMutation } from '@/app/[lng]/(workspace)/apps/stores/use-apps-store'
import { Button } from '@/components/base/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/base/dialog'
import { Input } from '@/components/base/input'
import { Label } from '@/components/base/label'
import { Textarea } from '@/components/base/textarea'
import { useTranslation } from '@/plugins/i18n/client'
import { Plus, Search } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

interface AppsHeaderProps {
  searchValue: string
  onSearchChange: (value: string) => void
}

function CreateAppDialog({ isOpen, onOpenChange }: { isOpen: boolean, onOpenChange: (open: boolean) => void }) {
  const { t } = useTranslation(['app', 'global'])
  const [newApp, setNewApp] = useState({ name: '', description: '' })
  const createApp = useCreateAppMutation()

  const handleCreateApp = async () => {
    try {
      await createApp.mutateAsync(newApp)
      onOpenChange(false)
      setNewApp({ name: '', description: '' })
      toast.success(t('global.text.create_successfully'))
    }
    catch (error) {
      console.error(error)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4" />
          {t('app.create_app')}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t('app.create_app')}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="name">{t('global.name')}</Label>
            <Input
              id="name"
              value={newApp.name}
              onChange={e => setNewApp(prev => ({ ...prev, name: e.target.value }))}
              placeholder={t('app.text.name_placeholder')}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="description">{t('app.description')}</Label>
            <Textarea
              id="description"
              value={newApp.description}
              onChange={e => setNewApp(prev => ({ ...prev, description: e.target.value }))}
              placeholder={t('app.text.description_placeholder')}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t('global.cancel')}
          </Button>
          <Button onClick={handleCreateApp} disabled={!newApp.name}>
            {t('global.create')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export function AppsHeader({ searchValue, onSearchChange }: AppsHeaderProps) {
  const { t } = useTranslation(['app', 'global'])
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="flex items-center justify-between gap-4 p-1">
      <div className="relative flex-1 max-w-sm">
        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          value={searchValue}
          placeholder={t('app.text.search_app')}
          className="pl-8"
          onChange={e => onSearchChange(e.target.value)}
        />
      </div>
      <CreateAppDialog isOpen={isOpen} onOpenChange={setIsOpen} />
    </div>
  )
}
