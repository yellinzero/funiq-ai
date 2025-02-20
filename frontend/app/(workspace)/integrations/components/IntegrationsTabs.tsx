'use client'

import { Box, Stack, Tab, Tabs } from '@mui/material'
import { usePathname, useRouter } from 'next/navigation'

interface IntegrationsTabsProps {
  labels: {
    label: string
    value: string
  }[]
  children?: React.ReactNode
}

export default function IntegrationsTabs({ labels, children }: IntegrationsTabsProps) {
  const router = useRouter()
  const pathname = usePathname()

  if (pathname === '/integrations') {
    return null
  }

  const handleTabChange = (_event: React.SyntheticEvent, newValue: string) => {
    router.push(newValue)
  }

  return (
    <Stack direction="row" spacing={2} justifyContent="space-between" alignItems="center" sx={{ px: 2 }}>
      <Tabs
        value={pathname}
        onChange={handleTabChange}
        sx={{
          mb: 3,
          flexGrow: 1,
         }}
      >
        {labels.map((label) => (
          <Tab
            key={label.value}
            label={label.label}
            value={label.value}
          />
        ))}
      </Tabs>
      {children && (
        <Box>
          {children}
        </Box>
      )}
    </Stack>
  )
}
