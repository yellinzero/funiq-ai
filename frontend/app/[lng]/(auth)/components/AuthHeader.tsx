'use client'

import LangSelect from '@/components/LangSelect'
import { Logo } from '@/components/SiteLogo'
import ThemeModeToggle from '@/components/ThemeModeToggle'
import { useRouter } from 'next/navigation'

export default function AuthHeader() {
  const router = useRouter()
  return (
    <header className="fixed top-0 w-full p-3 flex items-center justify-between">
      <Logo className="cursor-pointer" onClick={() => router.push('/')} />
      <div className="flex items-center">
        <LangSelect />
        <ThemeModeToggle />
      </div>
    </header>
  )
}
