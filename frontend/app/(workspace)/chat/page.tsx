'use client'

import { useTranslation } from 'react-i18next'

export default function Chat() {
  const { t } = useTranslation()

  return (
    <div className="flex flex-col items-center mx-12 pb-20 relative gap-8">
      <div className="text-center">
        {t('global.welcome', {
          name: t('global.product_name'),
        })}
      </div>
    </div>
  )
}
