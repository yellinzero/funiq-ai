'use client'

import { useTranslation } from '@/plugins/i18n/client'

export default function KnowledgeBase() {
  const { t } = useTranslation(['global'])

  return (
    <div className="flex flex-col items-center mx-12 pb-20 relative gap-8">
      <div className="text-center">
        app knowledge base
      </div>
    </div>
  )
}
