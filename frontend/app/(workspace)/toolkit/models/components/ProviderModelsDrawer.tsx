import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import FullPageLoading from '@/components/FullPageLoading'
import ModelCard from './ModelCard'
import { useModelsStore, useModelsQuery } from '@/app/(workspace)/toolkit/models/stores/useModelsStore'
import { useProviderQuery, useProviderStore } from '@/app/(workspace)/toolkit/models/stores/useProviderStore'
import { IModelInfo, IProviderInfo } from '@/apis/types'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetFooter,
} from '@/components/base/sheet'
import { Button } from '@/components/base/button'

interface ProviderModelsDrawerProps {
  provider: IProviderInfo
  open: boolean
  onClose: () => void
}

export default function ProviderModelsDrawer({ provider, open, onClose }: ProviderModelsDrawerProps) {
  const { i18n, t } = useTranslation()
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
        className="w-[40%] min-w-[600px] p-0 flex flex-col"
      >
        {/* Header */}
        <SheetHeader className="border-b p-4">
          <div className="flex items-center justify-between">
            <SheetTitle>{t('global.models')}</SheetTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </Button>
          </div>
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
