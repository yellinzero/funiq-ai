'use client'
import { Box, Grid2 } from '@mui/material'
import ProviderCard from '@/app/(workspace)/integrations/models/components/ProviderCard'
import ProviderModelsDrawer from '@/app/(workspace)/integrations/models/components/ProviderModelsDrawer'
import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import { RJSFSchema, UiSchema } from '@rjsf/utils'
import ProviderApiKeyDialog from './components/ProviderApiKeyDialog'
import FullPageLoading from '@/components/FullPageLoading'
import { useProvidersStore, useProvidersQuery } from './stores/useProvidersStore'
import { IProviderInfo } from '@/apis/types'

const namespaces = ['global', 'integrations']

export default function ModelsPage() {
  const { i18n } = useTranslation(namespaces)
  const { isLoading } = useProvidersQuery(i18n.language)
  const { providers } = useProvidersStore()
  const [openDrawer, setOpenDrawer] = useState(false)
  const [provider, setProvider] = useState<IProviderInfo | null>(null)
  const [providerLabel, setProviderLabel] = useState<string | null>(null)
  const [providerCredentialSchema, setProviderCredentialSchema] = useState<RJSFSchema | null>(null)
  const [providerCredentialUiSchema, setProviderCredentialUiSchema] = useState<UiSchema>()
  const [openApiKeyDialog, setOpenApiKeyDialog] = useState(false)

  if (isLoading) {
    return <FullPageLoading />
  }

  function handleClickModels(provider: IProviderInfo) {
    setProvider(provider)
    setOpenDrawer(true)
  }

  function handleClickAPIKey(provider: IProviderInfo) {
    setProviderLabel(provider.label)
    setProviderCredentialSchema(provider.credential_schema as RJSFSchema)
    setProviderCredentialUiSchema(provider.ui_schema?.credential_schema as UiSchema)
    setOpenApiKeyDialog(true)
  }

  return (
    <>
      <Box sx={{ p: 2, width: '100%', height: '100%', minWidth: 700 }}>
        <Grid2 container spacing={3} columns={12}>
          {providers.map((provider) => (
            <Grid2
              key={provider.provider}
              size={6}
              sx={{
                display: 'flex',
              }}
            >
              <ProviderCard key={provider.provider} {...provider} onClickModels={handleClickModels} onClickAPIKey={handleClickAPIKey} />
            </Grid2>
          ))}
        </Grid2>
      </Box>
      {provider && <ProviderModelsDrawer provider={provider} open={openDrawer} onClose={() => setOpenDrawer(false)} />}
      {providerLabel && providerCredentialSchema && <ProviderApiKeyDialog providerName={providerLabel} schema={providerCredentialSchema} uiSchema={providerCredentialUiSchema} open={openApiKeyDialog} onClose={() => setOpenApiKeyDialog(false)} />}
    </>
  )
}
