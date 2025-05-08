'use client'

import { usePathname, useRouter } from 'next/navigation'
import { cn } from '@/utils/ui'

interface IntegrationsTabsProps {
  labels: {
    label: string
    value: string
  }[]
  children?: React.ReactNode
}

export default function ToolkitTabs({ labels, children }: IntegrationsTabsProps) {
  const router = useRouter()
  const pathname = usePathname()

  if (pathname === '/toolkit') {
    return null
  }

  const handleTabChange = (value: string) => {
    router.push(value)
  }

  return (
    <div className="flex items-center justify-between gap-8 px-8">
      <div className="flex-1">
        <div className="flex space-x-1 border-b">
        {labels.map((label) => (
            <button
            key={label.value}
              onClick={() => handleTabChange(label.value)}
              className={cn(
                "inline-flex items-center justify-center whitespace-nowrap py-4 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
                "border-b-2 -mb-px",
                pathname === label.value
                  ? "border-primary text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              {label.label}
            </button>
        ))}
        </div>
      </div>
      {children && (
        <div>
          {children}
        </div>
      )}
    </div>
  )
}
