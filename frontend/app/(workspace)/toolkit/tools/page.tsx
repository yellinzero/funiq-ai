'use client'

import { useTranslation } from 'react-i18next'
import { Card, CardContent } from '@/components/base/card'
import { Button } from '@/components/base/button'
import { cn } from '@/utils/ui'

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
    <div className="p-4">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3">
        {tools.map((tool) => (
          <div key={tool.id}>
            <Card>
              <CardContent className="flex flex-col gap-4 p-6">
                <h3 className="text-lg font-semibold">
                  {tool.name}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {tool.description}
                </p>
                <Button
                  variant={tool.status === 'connected' ? 'outline' : 'default'}
                  className={cn(
                    tool.status === 'connected' && 'border-input hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  {tool.status === 'connected' ? t('disconnect') : t('connect')}
                </Button>
              </CardContent>
            </Card>
          </div>
        ))}
      </div>
    </div>
  )
}
