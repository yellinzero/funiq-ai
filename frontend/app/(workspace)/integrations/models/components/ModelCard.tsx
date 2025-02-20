import { Card, Stack, Typography, Chip, styled, Switch } from '@mui/material'
import { components } from '@/types/openapi'
import { capitalize } from 'lodash-es'

type AIModelEntity = components['schemas']['AIModelEntity']
type ProviderInfo = components['schemas']['ProviderInfo']

interface ModelCardProps extends AIModelEntity {
  icon: ProviderInfo['icon']
  onToggle?: (model: AIModelEntity, checked: boolean) => void
  enabled?: boolean
}

const StyledChip = styled(Chip)({
  borderRadius: 4,
  fontSize: '12px',
  height: '16px',
  color: 'text.secondary',
  '& .MuiChip-label': {
    px: 0.5,
  },
});

export default function ModelCard(props: ModelCardProps) {
  const {
    icon,
    onToggle,
    enabled = false,
    ...modelEntity
  } = props

  const {
    label,
    model_type,
    features = [],
    model_properties,
    deprecated = false,
  } = modelEntity

  const mode = (model_properties?.mode as string | undefined)?.toUpperCase()
  const contextSize = model_properties?.context_size ? (Number(model_properties.context_size) / 1000)?.toFixed(0) : undefined

  function getFeatureLabel(feature: string) {
    return capitalize(feature.replaceAll('-', ' '))
  }

  return (
    <Card
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        opacity: deprecated ? 0.6 : 1,
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Stack direction="row" alignItems="center" gap={1} sx={{ flexGrow: 1, justifyContent: 'space-between' }}>
        <Stack direction="row" alignItems="center" gap={1}>
          <Typography variant="subtitle2" fontWeight="medium" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {icon?.small && (
              <img
                src={icon.small}
                alt={label}
                height={24}
                width={24}
                style={{ objectFit: 'contain' }}
              />
            )}
            {label}
          </Typography>
          <Stack direction="row" gap={0.5}>
            <StyledChip
              label={model_type.toUpperCase()}
              size="small"
              variant="outlined"
            />
            {mode && <StyledChip
              label={mode}
              size="small"
              variant="outlined"
            />}
            {contextSize && <StyledChip
              label={`${contextSize}K`}
              size="small"
              variant="outlined"
            />}
          </Stack>
        </Stack>
        {onToggle && (
          <Switch
            checked={enabled}
            onChange={(e) => onToggle(modelEntity, e.target.checked)}
            size="small"
            disabled={deprecated}
          />
        )}
      </Stack>

      {features && features.length > 0 && (
        <Stack direction="row" flexWrap="wrap" gap={0.5}>
          {features.map((feature) => (
            <StyledChip
              key={feature}
              label={getFeatureLabel(feature)}
              size="small"
            />
          ))}
        </Stack>
      )}
    </Card>
  )
}
