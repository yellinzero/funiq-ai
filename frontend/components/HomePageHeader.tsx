'use client'

import LangSelect from './LangSelect'
import ThemeModeToggle from './ThemeModeToggle'

export default function HomePageHeader() {
  return (
    <div className="flex w-full items-center justify-end px-2 pt-2">
      <div className="flex items-center">
        <LangSelect />
        <ThemeModeToggle />
      </div>
    </div>
  )
}
