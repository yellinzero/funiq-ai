import { Button, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material'
import { RJSFSchema, UiSchema } from '@rjsf/utils';
import { useTranslation } from 'react-i18next';
import React from 'react';
import type FormType from '@rjsf/core';
import JsonSchemaForm from '@/components/JsonSchemaForm';
import { useProviderMutation, useProviderQuery } from '../stores/useProviderStore';

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
          is_system: providerData?.is_system ?? false,
          credentials: formData
        })
        onClose()
      } catch (error) {
        console.error('Failed to save provider credentials:', error)
      }
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      scroll="paper"
    >
      <DialogTitle>{providerName} {t('api_key', { ns: 'integrations' })}</DialogTitle>
      <DialogContent sx={{ overflow: 'hidden', width: '100%' }}>
        <JsonSchemaForm
          ref={formRef}
          formData={formData}
          onChange={(e) => setFormData(e.formData)}
          schema={schema}
          uiSchema={uiSchema}
          locale={i18n.language}
        />
      </DialogContent>
      <DialogActions sx={{ pb: 3, px: 2 }}>
        <Button onClick={onClose}>{t('cancel', { ns: 'global' })}</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          {t('save', { ns: 'global' })}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
