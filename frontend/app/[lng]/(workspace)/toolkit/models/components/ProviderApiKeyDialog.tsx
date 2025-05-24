import type { IProviderInfo } from '@/apis'
import type FormType from '@rjsf/core'
import type { RJSFSchema, UiSchema } from '@rjsf/utils'
import { useProviderMutation, useProviderQuery } from '@/app/[lng]/(workspace)/toolkit/models/stores/use-provider-store'
import { Button } from '@/components/base/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/base/dialog'
import JsonSchemaForm from '@/components/JsonSchemaForm'
import { useTranslation } from '@/plugins/i18n/client'
import { Loader2 } from 'lucide-react'
import React from 'react'

interface ProviderApiKeyDialogProps {
  provider: IProviderInfo
  open: boolean
  onClose: () => void
}

export default function ProviderApiKeyDialog({
  provider,
  open,
  onClose,
}: ProviderApiKeyDialogProps) {
  const { t, i18n } = useTranslation(['global', 'toolkit'])
  const formRef = React.useRef<FormType>(null)
  const { data: providerData } = useProviderQuery(open ? provider.provider : '')
  const { mutateAsync: saveProvider, isPending } = useProviderMutation(provider.provider)
  const [formData, setFormData] = React.useState({})
  const schema = provider.config_schema?.json_schema as RJSFSchema
  const uiSchema = provider.config_schema?.ui_schema as UiSchema
  React.useEffect(() => {
    if (providerData?.credentials) {
      setFormData(providerData.credentials)
    }
  }, [providerData])

  const handleSubmit = async () => {
    if (formRef.current) {
      try {
        await saveProvider({
          credentials: formData,
        })
        handleClose()
      }
      catch (error) {
        console.error('Failed to save provider credentials:', error)
      }
    }
  }

  function handleClose() {
    if (isPending)
      return
    setFormData({})
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {provider.label}
            {' '}
            {t('toolkit.api_key')}
          </DialogTitle>
        </DialogHeader>

        <div className="overflow-hidden w-full">
          <JsonSchemaForm
            ref={formRef}
            formData={formData}
            onChange={e => setFormData(e.formData)}
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
