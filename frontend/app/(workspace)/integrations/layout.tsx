import { Box, Tab, Tabs } from '@mui/material'
import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import { getLocaleFromServer } from '@/plugins/i18n/server'
import { initTranslations } from '@/plugins/i18n'
import IntegrationsTabs from './components/IntegrationsTabs'

const namespaces = ['global']
export default async function IntegrationsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const locale = await getLocaleFromServer()
  const { t } = await initTranslations(locale, namespaces)
  const labels = [
    {
      label: t('models', { ns: 'global' }),
      value: '/integrations/models',
    },
    {
      label: t('tools', { ns: 'global' }),
      value: '/integrations/tools',
    },
  ]

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
      <IntegrationsTabs labels={labels} />
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {children}
      </Box>
    </Box>
  )
}
