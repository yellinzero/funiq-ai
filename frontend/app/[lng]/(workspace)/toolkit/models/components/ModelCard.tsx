import type { IModelInfo, IProviderInfo } from '@/apis'
import { Card, CardContent } from '@/components/base/card'
import { cn } from '@/utils/ui'
import { capitalize } from 'lodash-es'

interface ModelCardProps extends IModelInfo {
  icon: IProviderInfo['icon']
  disabled?: boolean
  onToggle?: (model: IModelInfo, checked: boolean) => void
}

function Chip({
  label,
  variant = 'default',
  className,
}: {
  label: string
  variant?: 'default' | 'outline'
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium transition-colors',
        variant === 'default' && 'bg-primary/10 text-primary',
        variant === 'outline' && 'border border-input bg-background text-muted-foreground',
        className,
      )}
    >
      {label}
    </span>
  )
}

export default function ModelCard(props: ModelCardProps) {
  const {
    icon,
    onToggle,
    disabled,
    ...modelInfo
  } = props

  const {
    label,
    model_type,
    features = [],
    model_properties,
    deprecated = false,
  } = modelInfo

  const mode = (model_properties?.mode as string | undefined)?.toUpperCase()
  const contextSize = model_properties?.context_size
    ? (Number(model_properties.context_size) / 1000)?.toFixed(0)
    : undefined

  function getFeatureLabel(feature: string) {
    return capitalize(feature.replaceAll('-', ' '))
  }

  return (
    <Card className={cn(
      'p-4 flex flex-col gap-2',
      deprecated && 'opacity-60',
    )}
    >
      <CardContent className="p-0">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 font-medium">
              {icon?.small && (
                <img
                  src={icon.small}
                  alt={label}
                  className="h-6 w-6 object-contain"
                />
              )}
              <span>{label}</span>
            </div>
            <div className="flex gap-1">
              <Chip
                label={model_type.toUpperCase()}
                variant="outline"
              />
              {mode && (
                <Chip
                  label={mode}
                  variant="outline"
                />
              )}
              {contextSize && (
                <Chip
                  label={`${contextSize}K`}
                  variant="outline"
                />
              )}
            </div>
          </div>
        </div>

        {features && features.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {features.map(feature => (
              <Chip
                key={feature}
                label={getFeatureLabel(feature)}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
