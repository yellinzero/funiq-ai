'use client'
import PureLogoGraySvg from '@/assets/icons/pure-logo-gray.svg?url'
import PureLogoWhiteSvg from '@/assets/icons/pure-logo-white.svg?url'
import LogoGraySvg from '@/assets/icons/logo-gray.svg?url'
import LogoWhiteSvg from '@/assets/icons/logo-white.svg?url'
import Image from 'next/image'
import { useCookies } from 'react-cookie'

export function LogoWithName(props: {
  height?: number
  width?: number
}) {
  const { height = 40, width } = props
  // Get theme from cookies on server side
  const [_cookie] = useCookies()

  const theme = _cookie.theme
  return (
    <Image
      src={theme === 'dark' ? LogoWhiteSvg : LogoGraySvg}
      height={height} width={width}
      alt="Logo"
      priority
    />
  )
}

export function Logo(props: {
  height?: number
  width?: number
}) {
  const { height = 40, width } = props
  // Get theme from cookies on server side
  const [_cookie] = useCookies()

  const theme = _cookie.theme
  return (
    <Image
      src={theme === 'dark' ? PureLogoWhiteSvg : PureLogoGraySvg}
      height={height} width={width}
      alt="Logo"
      priority
    />
  )
}
