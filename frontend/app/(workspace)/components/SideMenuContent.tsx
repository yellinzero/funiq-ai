'use client'
import { AccountTree, Hub, QuestionAnswer, Storefront } from '@mui/icons-material'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import Stack from '@mui/material/Stack'
import { useTranslation } from 'react-i18next'
import Tooltip from '@mui/material/Tooltip'
import { useRouter, usePathname } from 'next/navigation'

interface Props {
  expanded: boolean
  showContent: boolean
}

export default function SideMenuContent({ expanded, showContent }: Props) {
  const { t } = useTranslation()
  const router = useRouter()
  const pathname = usePathname()

  const isSelected = (path: string) => {
    return pathname?.startsWith(path) ?? false
  }

  const mainListItems = [
    { text: t('chats', { ns: 'global' }), icon: <QuestionAnswer />, path: '/chat' },
    { text: t('workflows', { ns: 'global' }), icon: <AccountTree />, path: '/workflows' },
    { text: t('store', { ns: 'global' }), icon: <Storefront />, path: '/store' },
    { text: t('integrations', { ns: 'global' }), icon: <Hub />, path: '/integrations' },
  ]

  const gotoPage = (page: string) => {
    router.push(page)
  }

  return (
    <Stack sx={{ flexGrow: 1, px: 1, justifyContent: 'space-between', width: '100%' }}>
      <List dense>
        {mainListItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            {expanded ? (
              <ListItemButton
                selected={isSelected(item.path)}
                sx={{ height: 36 }}
                onClick={() => gotoPage(item.path)}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
                {showContent && <ListItemText primary={item.text} />}
              </ListItemButton>
            ) : (
              <Tooltip title={item.text} placement="right" onClick={() => gotoPage(item.path)}>
                <ListItemButton
                  selected={isSelected(item.path)}
                  sx={{
                    width: 36,
                    height: 36,
                    justifyContent: 'center',
                    px: 2.5,
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      justifyContent: 'center',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                </ListItemButton>
              </Tooltip>
            )}
          </ListItem>
        ))}
      </List>
    </Stack>
  )
}
