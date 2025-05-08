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
  const { mutate: saveProvider } = useProviderMutation(providerName)
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
        onClose()
      } catch (error) {
        console.error('Failed to save provider credentials:', error)
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
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

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={onClose}
          >
            {t('global.cancel')}
          </Button>
          <Button
            onClick={handleSubmit}
          >
            {t('global.save')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
