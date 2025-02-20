'use client'
import type { Metadata } from 'next'
import { createTheme } from '@mui/material/styles'
import { colorSchemes, shape, typography } from './themePrimitives'



export const metadata: Metadata = {
  title: 'Funiq AI',
  description: 'AI with fun',
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export const theme = createTheme({
  typography,
  colorSchemes, // Recently added in v6 for building light & dark mode app, see https://mui.com/material-ui/customization/palette/#color-schemes
  shape,
})
