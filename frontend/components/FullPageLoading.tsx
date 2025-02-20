import { Box, CircularProgress } from '@mui/material'
export default function FullPageLoading() {
  return (
    <Box sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100%',
      width: '100%',
    }}>
      <CircularProgress />
    </Box>
  )
}
