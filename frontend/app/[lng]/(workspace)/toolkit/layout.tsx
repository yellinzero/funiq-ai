import { getTranslation } from '@/plugins/i18n'
import ToolkitTabs from './components/ToolkitTabs'

const namespaces = ['global']

export default async function IntegrationsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { t } = await getTranslation(namespaces)
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
