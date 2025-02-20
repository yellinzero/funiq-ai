'use client'
import ColorModeIconDropdown from '@/theme/ColorModeIconDropdown'
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded'
import Stack from '@mui/material/Stack'
import MenuButton from '../../components/SideMenuButton'

export default function Header() {
  return (
    <Stack
      direction="row"
      sx={{
        display: 'flex',
        width: '100%',
        alignItems: 'center',
        justifyContent: 'right',
        pt: 1.5,
      }}
      spacing={2}
    >
      <Stack direction="row" sx={{ gap: 1 }}>
        <MenuButton showBadge aria-label="Open notifications">
          <NotificationsRoundedIcon />
        </MenuButton>
        <ColorModeIconDropdown />
      </Stack>
    </Stack>
  )
}
