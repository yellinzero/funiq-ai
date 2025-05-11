import { useTranslation } from '@/plugins/i18n/client'
import { useEffect, useState } from 'react'
import FullPageLoading from '@/components/FullPageLoading'
import ModelCard from './ModelCard'
import { useModelsStore, useModelsQuery } from '@/app/[lng]/(workspace)/toolkit/models/stores/useModelsStore'
import { useProviderQuery, useProviderStore } from '@/app/[lng]/(workspace)/toolkit/models/stores/useProviderStore'
import { IModelInfo, IProviderInfo } from '@/apis/types'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetFooter,
} from '@/components/base/sheet'

interface ProviderModelsDrawerProps {
  provider: IProviderInfo
  open: boolean
  onClose: () => void
}

export default function ProviderModelsSheet({ provider, open, onClose }: ProviderModelsDrawerProps) {
  const { t, i18n } = useTranslation(['global', 'toolkit'])
  const { setCurrentProvider } = useModelsStore()
  const { isLoading: isModelsLoading, refetch: refetchModels } = useModelsQuery(open ? provider.provider : null, i18n.language)
  const { isLoading: isProviderLoading } = useProviderQuery(open ? provider.provider : '')
  const { models } = useModelsStore()
  const { provider: currentProvider } = useProviderStore()
  const [isProviderUnavailable, setIsProviderUnavailable] = useState(false)

  useEffect(() => {
    setCurrentProvider(open ? provider : null)
  }, [open, provider])

  useEffect(() => {
    setIsProviderUnavailable(!currentProvider)
  }, [currentProvider])

  const providerModels = models[provider.provider] || []
  const isLoading = isModelsLoading || isProviderLoading

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent
        side="right"
        className="w-[40%] p-0 flex flex-col"
      >
        {/* Header */}
        <SheetHeader className="border-b p-4">
          <SheetTitle>{t('global.models')}</SheetTitle>
        </SheetHeader>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {isLoading ? (
            <FullPageLoading />
          ) : (
            <div className="grid gap-4">
              {providerModels.map((model: IModelInfo) => (
                <div key={model.model}>
                  <ModelCard {...model} icon={provider.icon} disabled={isProviderUnavailable} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <SheetFooter className="border-t p-4">
          <div className="flex w-full items-center">
            <p className="text-sm text-muted-foreground">
              {t('toolkit.count_models', { count: providerModels.length })}
            </p>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
