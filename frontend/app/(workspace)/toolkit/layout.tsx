import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import { getLocaleFromServer } from '@/plugins/i18n/server'
import { initTranslations } from '@/plugins/i18n'
import ToolkitTabs from './components/ToolkitTabs'

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
      label: t('global.models'),
      value: '/toolkit/models',
    },
    // {
    //   label: t('global.tools'),
    //   value: '/toolkit/tools',
    // },
  ]

  return (
    <div className="flex h-full w-full flex-col">
      <ToolkitTabs labels={labels} />
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  )
}
