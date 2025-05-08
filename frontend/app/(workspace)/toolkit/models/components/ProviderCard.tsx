import { useTranslation } from 'react-i18next'
import { IProviderInfo } from '@/apis/types'
import { Card, CardContent } from '@/components/base/card'
import { Button } from '@/components/base/button'
import { cn } from '@/utils/ui'

export type ProviderCardProps = IProviderInfo & {
  onClickAPIKey?: (provider: IProviderInfo) => void
  onClickModels?: (provider: IProviderInfo) => void
}

function Chip({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
      {label}
    </span>
  )
}

export default function ProviderCard(props: ProviderCardProps) {
  const { t } = useTranslation()
  const {
    label,
    description,
    model_types,
    icon,
    onClickAPIKey,
    onClickModels,
  } = props

  return (
    <Card className="flex min-w-[300px] flex-1 flex-col gap-4 overflow-auto p-4">
      <CardContent className="p-0">
        <div className="flex flex-wrap items-center justify-between gap-4">
        {icon?.large && (
          <img
            src={icon.large}
            alt={label}
              className="h-6 object-contain"
          />
        )}
          <div className="flex items-center gap-2">
          <Button
              variant="outline"
              size="sm"
              className="min-w-[100px]"
            onClick={() => onClickAPIKey?.(props)}
          >
            {t('toolkit.api_key')}
          </Button>
          <Button
              variant="outline"
              size="sm"
              className="min-w-[100px]"
            onClick={() => onClickModels?.(props)}
          >
            {t('toolkit.configure_models')}
          </Button>
          </div>
        </div>

        <p className="mt-4 text-sm text-muted-foreground">
        {description}
        </p>

        <div className="mt-4 flex flex-wrap items-center gap-1">
        {model_types.map((type) => (
          <Chip
            key={type}
            label={type.toUpperCase()}
          />
        ))}
        </div>
      </CardContent>
    </Card>
  )
}
