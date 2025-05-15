'use client'

import { useTranslation } from '@/plugins/i18n/client'

export default function Chat() {
  const { t } = useTranslation(['global'])

  return (
    <div className="flex flex-col items-center mx-12 pb-20 relative gap-8">
      <div className="text-center">
        {t('global.text.welcome', {
          name: t('global.product_name'),
        })}
      </div>
    </div>
  )
}
