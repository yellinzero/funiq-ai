import { getCurrentUser } from '@/apis'
import { Button } from '@/components/base/button'
import CurrentUserInfoBox from '@/components/CurrentUserInfoBox'
import HomePageHeader from '@/components/HomePageHeader'
import { Logo } from '@/components/SiteLogo'
import { getTranslation } from '@/plugins/i18n'
import Link from 'next/link'

export default async function Home() {
  const { t } = await getTranslation(['global'])

  const userInfo = await getCurrentUser()

  return (
    <main className="w-screen h-screen bg-background flex flex-col">
      <HomePageHeader />

      <div className="flex-1 flex flex-col justify-center items-center gap-8 px-4">
        <Logo className="h-[120px] w-[360px]" />

        <p className="text-muted-foreground text-center max-w-[600px] text-lg sm:text-xl">
          {t('global.text.home_description')}
        </p>

        {userInfo && (
          <Link href="/chat" className="no-underline">
            <CurrentUserInfoBox userInfo={userInfo} showName />
          </Link>
        )}

        {!userInfo && (
          <div className="flex flex-col gap-2 items-center">
            <Link href="/sign-in">
              <Button
                size="lg"
                className="px-8 py-2 text-lg rounded-lg"
              >
                {t('global.sign_in')}
              </Button>
            </Link>

            <Link href="/sign-up">
              <Button
                variant="ghost"
                className="text-muted-foreground hover:text-foreground"
              >
                {t('global.sign_up')}
              </Button>
            </Link>
          </div>
        )}
      </div>
    </main>
  )
}
