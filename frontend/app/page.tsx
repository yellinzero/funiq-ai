'use client'
import AppNavbar from '@/components/AppNavbar'
import Header from '@/components/Header'
import SideMenu from '@/components/SideMenu'
import AppTheme from '@/theme/AppTheme'
import Box from '@mui/material/Box'
import CssBaseline from '@mui/material/CssBaseline'
import Stack from '@mui/material/Stack'
import { alpha } from '@mui/material/styles'

export default function Home(props: { disableCustomTheme?: boolean }) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: 'flex', height: '100vh', width: '100vw' }}>
        <SideMenu />
        <AppNavbar />
        {/* Main content */}
        <Box
          component="main"
          sx={theme => ({
            flexGrow: 1,
            backgroundColor: theme.vars
              ? `rgba(${theme.vars.palette.background.defaultChannel} / 1)`
              : alpha(theme.palette.background.default, 1),
            overflow: 'auto',
          })}
        >
          <Stack
            spacing={2}
            sx={{
              alignItems: 'center',
              mx: 3,
              pb: 5,
              mt: { xs: 8, md: 0 },

            }}
          >
            <Header />
            <div>Hello world </div>
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  )
}
