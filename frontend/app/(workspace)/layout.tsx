import { meOptions } from '@/apis'
import SideMenu from '@/app/(workspace)/components/SideMenu'
import { getQueryClient } from '@/utils/get-query-client'
import Box from '@mui/material/Box'

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient()

  void queryClient.prefetchQuery(meOptions)
  return (
    <Box sx={{ display: 'flex', height: '100vh', width: '100vw' }}>
      <SideMenu />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          backgroundColor: 'background.default',
          overflow: 'auto',
        }}
      >
        {children}
      </Box>
    </Box>
  )
}
