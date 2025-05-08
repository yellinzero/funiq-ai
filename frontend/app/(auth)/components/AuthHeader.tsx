'use client'

import LangSelect from '@/components/LangSelect'
import { LogoWithName } from '@/components/SiteLogo'
import ThemeModeToggle from '@/components/ThemeModeToggle'

export default function AuthHeader() {
  return (
    <header className="fixed top-0 w-full p-3 flex items-center justify-between">
      <LogoWithName />
      <div className="flex items-center">
        <LangSelect />
        <ThemeModeToggle />
      </div>
    </header>
  )
}
