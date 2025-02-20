'use client'
import { Box, Stack } from '@mui/material'
import { useTranslation } from 'react-i18next'
import ChatHeader from './components/ChatHeader'

export default function Chat() {
  const { t } = useTranslation()
  return (
    <Stack
      spacing={2}
      sx={{
        alignItems: 'center',
        mx: 3,
        pb: 5,
        position: 'relative',
      }}
    >
      <ChatHeader />
      {t('welcome', {
        name: t('product_name', { ns: 'global' }),
        ns: 'global',
      })}
    </Stack>
  )
}
