'use client'

import { usePathname, useRouter } from 'next/navigation'
import {
  Tabs,
  TabsList,
  TabsTrigger,
} from "@/components/base/tabs"

interface ToolkitTabsProps {
  labels: {
    label: string
    value: string
  }[]
  children?: React.ReactNode
}

export default function ToolkitTabs({ labels, children }: ToolkitTabsProps) {
  const router = useRouter()
  const pathname = usePathname()

  if (pathname === '/toolkit') {
    return null
  }

  const handleTabChange = (value: string) => {
    router.push(value)
  }

  return (
    <div className="border-b">
      <div className="container">
        <Tabs
          value={pathname}
          onValueChange={handleTabChange}
          className="w-full"
        >
          <TabsList className="h-auto justify-start gap-6 bg-transparent p-0">
            {labels.map((label) => (
              <TabsTrigger
                key={label.value}
                value={label.value}
                className="cursor-pointer relative h-12 rounded-none border-0 bg-transparent px-2 font-medium data-[state=active]:bg-transparent data-[state=active]:shadow-none before:absolute before:bottom-0 before:left-0 before:h-0.5 before:w-full before:bg-transparent data-[state=active]:before:bg-primary"
              >
                {label.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>
    </div>
  )
}
