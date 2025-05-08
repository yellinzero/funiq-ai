'use client'

import ProviderCard from '@/app/(workspace)/toolkit/models/components/ProviderCard'
import ProviderModelsDrawer from '@/app/(workspace)/toolkit/models/components/ProviderModelsDrawer'
import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import { RJSFSchema, UiSchema } from '@rjsf/utils'
import ProviderApiKeyDialog from './components/ProviderApiKeyDialog'
import FullPageLoading from '@/components/FullPageLoading'
import { useProvidersStore, useProvidersQuery } from './stores/useProvidersStore'
import { IProviderInfo } from '@/apis/types'

const namespaces = ['global', 'toolkit']

export default function ModelsPage() {
  const { i18n } = useTranslation(namespaces)
  const { isLoading } = useProvidersQuery(i18n.language)
  const { providers } = useProvidersStore()
  const [openDrawer, setOpenDrawer] = useState(false)
  const [openApiKeyDialog, setOpenApiKeyDialog] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState<IProviderInfo | null>(null)

  if (isLoading) {
    return <FullPageLoading />
  }

  function handleClickModels(provider: IProviderInfo) {
    setSelectedProvider(provider)
    setOpenDrawer(true)
  }

  function handleClickAPIKey(provider: IProviderInfo) {
    setSelectedProvider(provider)
    setOpenApiKeyDialog(true)
  }

  return (
    <>
      <div className="h-full w-full min-w-[700px] p-4">
        <div className="grid grid-cols-2 gap-6">
          {providers.map((provider) => (
            <div
              key={provider.provider}
              className="flex"
            >
              <ProviderCard
                {...provider}
                onClickModels={handleClickModels}
                onClickAPIKey={handleClickAPIKey}
              />
            </div>
          ))}
        </div>
      </div>

      {selectedProvider && (
        <>
          <ProviderModelsDrawer
            provider={selectedProvider}
            open={openDrawer}
            onClose={() => setOpenDrawer(false)}
          />
          {selectedProvider.config_schema && (
            <ProviderApiKeyDialog
              providerName={selectedProvider.provider}
              schema={selectedProvider.config_schema?.json_schema as RJSFSchema}
              uiSchema={selectedProvider.config_schema?.ui_schema as UiSchema}
              open={openApiKeyDialog}
              onClose={() => setOpenApiKeyDialog(false)}
            />
          )}
        </>
      )}
    </>
  )
}
