import { Box, Button, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material'
import Form from '@rjsf/mui';
import { RJSFSchema, UiSchema } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';
import { useTranslation } from 'react-i18next';
import React from 'react';
import JsonSchemaForm from '@/components/JsonSchemaForm';

interface ProviderApiKeyDialogProps {
  providerName: string
  schema: RJSFSchema
  uiSchema?: UiSchema
  open: boolean
  onClose: () => void
}

export default function ProviderApiKeyDialog({ providerName, schema, uiSchema, open, onClose }: ProviderApiKeyDialogProps) {
  const { t } = useTranslation()
  const formRef = React.useRef<any>()

  const handleSubmit = () => {
    if (formRef.current) {
      formRef.current.submit()
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
          schema={schema}
          uiSchema={uiSchema}
          validator={validator}
        />
      </DialogContent>
      <DialogActions sx={{ pb: 3, px: 2 }}>
        <Button onClick={onClose}>{t('cancel', { ns: 'global' })}</Button>
        <Button onClick={handleSubmit}>{t('save', { ns: 'global' })}</Button>
      </DialogActions>
    </Dialog>
  )
}
