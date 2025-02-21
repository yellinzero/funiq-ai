import { Box, Card, CardContent, Typography, Button, Chip, Stack, CardActions } from '@mui/material'
import { useTranslation } from 'react-i18next'
import { IProviderInfo } from '@/apis/types'

export type ProviderCardProps = IProviderInfo & {
  onClickAPIKey?: (provider: IProviderInfo) => void
  onClickModels?: (provider: IProviderInfo) => void
}

export default function ProviderCard(props: ProviderCardProps) {
  const { t } = useTranslation()
  const {
    label,
    description,
    supported_model_types,
    icon,
    onClickAPIKey,
    onClickModels,
  } = props


  return (
    <Card sx={{
      display: 'flex',
      flexDirection: 'column',
      gap: 2,
      overflow: 'auto',
      p: 2,
      flexGrow: 1,
      minWidth: 300,
    }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={1}>
        {icon?.large && (
          <img
            src={icon.large}
            alt={label}
            height={24}
            style={{ objectFit: 'contain' }}
          />
        )}
        <Stack direction="row" spacing={1} alignItems="center">
          <Button
            variant="outlined"
            size="small"
            sx={{ minWidth: 100 }}
            onClick={() => onClickAPIKey?.(props)}
          >
            {t('api_key', { ns: 'integrations' })}
          </Button>
          <Button
            variant="outlined"
            size="small"
            sx={{ minWidth: 100 }}
            onClick={() => onClickModels?.(props)}
          >
            {t('configure_models', { ns: 'integrations' })}
          </Button>
        </Stack>
      </Stack>
      <Typography variant="body2" color="text.secondary">
        {description}
      </Typography>
      <Stack direction="row" alignItems="center" flexWrap="wrap" gap={0.5}>
        {supported_model_types.map((type) => (
          <Chip
            key={type}
            label={type.toUpperCase()}
            size="small"
          />
        ))}
      </Stack>
    </Card>
  )
}
