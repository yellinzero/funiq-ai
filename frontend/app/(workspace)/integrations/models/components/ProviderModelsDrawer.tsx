import { Box, Drawer, Grid2, Typography, IconButton, Stack, Button } from '@mui/material'
import { useTranslation } from 'react-i18next'
import { useEffect } from 'react'
import FullPageLoading from '@/components/FullPageLoading'
import ModelCard from './ModelCard'
import { useModelsStore, useModelsQuery } from '@/app/(workspace)/integrations/models/stores/useModelsStore'
import { components } from '@/types/openapi'
import CloseIcon from '@mui/icons-material/Close'

type ProviderInfo = components['schemas']['ProviderInfo']
type AIModelEntity = components['schemas']['AIModelEntity']

interface ProviderModelsDrawerProps {
  provider: ProviderInfo
  open: boolean
  onClose: () => void
}

export default function ProviderModelsDrawer({ provider, open, onClose }: ProviderModelsDrawerProps) {
  const { i18n, t } = useTranslation()
  const { setCurrentProvider } = useModelsStore()
  const { isLoading } = useModelsQuery(open ? provider.provider : null, i18n.language)
  const { models } = useModelsStore()

  useEffect(() => {
    setCurrentProvider(open ? provider : null)
  }, [open, provider])

  const providerModels = models[provider.provider] || []

  const canAddModel = provider.configurate_methods.includes('customizable')
  function handleToggle(model: AIModelEntity, enabled: boolean) {
    console.log(model, enabled)
  }

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: '40%',
          minWidth: '600px',
        },
      }}
    >
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">{t('models', { ns: 'global' })}</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Stack>
      </Box>

      {/* Content */}
      <Box sx={{ p: 2, height: 'calc(100% - 120px)', overflow: 'auto' }}>
        {isLoading ? (
          <FullPageLoading />
        ) : (
          <Grid2 container spacing={2}>
            {providerModels.map((model: AIModelEntity) => (
              <Grid2 size={12} key={model.model}>
                <ModelCard {...model} icon={provider.icon} onToggle={handleToggle} />
              </Grid2>
            ))}
          </Grid2>
        )}
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', mt: 'auto' }}>
        <Stack direction="row" alignItems="center">
          <Typography variant="body2" color="text.secondary" sx={{
            flexGrow: 1,
          }}>
            {t('count_models', { ns: 'integrations', count: providerModels.length })}
          </Typography>
          {canAddModel && (
            <Button variant="contained" color="primary">
              {t('add_model', { ns: 'integrations' })}
            </Button>
          )}
        </Stack>
      </Box>
    </Drawer>
  )
}
