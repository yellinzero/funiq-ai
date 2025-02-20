'use client'
import { Box, Card, CardContent, Typography, Grid2, Button } from '@mui/material'
import { useTranslation } from 'react-i18next'

interface ToolCard {
  id: string
  name: string
  description: string
  status: 'connected' | 'available'
}

export default function ToolsPage() {
  const { t } = useTranslation(['global'])

  // This would typically come from an API
  const tools: ToolCard[] = [
    {
      id: 'google-calendar',
      name: 'Google Calendar',
      description: 'Manage your calendar and schedule meetings',
      status: 'available',
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Connect with your Slack workspace',
      status: 'connected',
    },
    // Add more tools as needed
  ]

  return (
    <Box sx={{ p: 2 }}>
      <Grid2 container spacing={3}>
        {tools.map((tool) => (
          <Grid2 sx={{ xs: 12, sm: 6, md: 4 }} key={tool.id}>
            <Card>
              <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Typography variant="h6">{tool.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {tool.description}
                </Typography>
                <Button
                  variant={tool.status === 'connected' ? 'outlined' : 'contained'}
                  color={tool.status === 'connected' ? 'inherit' : 'primary'}
                >
                  {tool.status === 'connected' ? t('disconnect') : t('connect')}
                </Button>
              </CardContent>
            </Card>
          </Grid2>
        ))}
      </Grid2>
    </Box>
  )
}
