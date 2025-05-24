'use client'

import type { IAppInfo } from '@/apis'
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
import { type ReactNode, useState } from 'react'

interface AppEditDialogProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: { name: string, description: string }) => Promise<void>
  mode: 'create' | 'edit'
  trigger?: ReactNode
  appInfo?: Partial<IAppInfo>
}

export function AppEditDialog({
  isOpen,
  onOpenChange,
  onSubmit,
  mode,
  trigger,
  appInfo,
}: AppEditDialogProps) {
  const { t } = useTranslation(['app', 'global'])
  const [formData, setFormData] = useState({
    name: appInfo?.name ?? '',
    description: appInfo?.description ?? '',
  })

  const handleSubmit = async () => {
    try {
      await onSubmit(formData)
      onOpenChange(false)
      setFormData({ name: '', description: '' })
    }
    catch (error) {
      console.error(error)
    }
  }

  const isCreate = mode === 'create'

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {isCreate ? t('app.create_app') : t('app.edit_app')}
          </DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="name">{t('global.name')}</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder={t('app.text.name_placeholder')}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="description">{t('app.description')}</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder={t('app.text.description_placeholder')}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t('global.cancel')}
          </Button>
          <Button onClick={handleSubmit} disabled={!formData.name}>
            {isCreate ? t('global.create') : t('global.save')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
