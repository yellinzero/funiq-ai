import { RJSFSchema, UiSchema } from '@rjsf/utils'
import { useTranslation } from 'react-i18next'
import React from 'react'
import type FormType from '@rjsf/core'
import JsonSchemaForm from '@/components/JsonSchemaForm'
import { useProviderMutation, useProviderQuery } from '../stores/useProviderStore'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/base/dialog'
import { Button } from '@/components/base/button'
import { Loader2 } from 'lucide-react'

interface ProviderApiKeyDialogProps {
  providerName: string
  schema: RJSFSchema
  uiSchema?: UiSchema
  open: boolean
  onClose: () => void
}

export default function ProviderApiKeyDialog({
  providerName,
  schema,
  uiSchema,
  open,
  onClose,
}: ProviderApiKeyDialogProps) {
  const { t, i18n } = useTranslation()
  const formRef = React.useRef<FormType>(null)
  const { data: providerData } = useProviderQuery(open ? providerName : '')
  const { mutateAsync: saveProvider, isPending } = useProviderMutation(providerName)
  const [formData, setFormData] = React.useState({})

  React.useEffect(() => {
    if (providerData?.credentials) {
      setFormData(providerData.credentials)
    }
  }, [providerData])

  const handleSubmit = async () => {
    if (formRef.current) {
      try {
        await saveProvider({
          credentials: formData
        })
        handleClose()
      } catch (error) {
        console.error('Failed to save provider credentials:', error)
      }
    }
  }

  const handleClose = () => {
    if (isPending) return
    setFormData({})
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {providerName} {t('toolkit.api_key')}
          </DialogTitle>
        </DialogHeader>

        <div className="overflow-hidden w-full">
          <JsonSchemaForm
            ref={formRef}
            formData={formData}
            onChange={(e) => setFormData(e.formData)}
            schema={schema}
            uiSchema={uiSchema}
            locale={i18n.language}
          />
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isPending}
          >
            {t('global.cancel')}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isPending}
          >
            {isPending && <Loader2 className="animate-spin" />}
            {t('global.save')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
