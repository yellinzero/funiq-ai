import { getAccountInfoApi } from '@/apis/openapis/account'
import CurrentUserInfoBox from '@/components/CurrentUserInfoBox'
import HomePageHeader from '@/components/HomePageHeader'
import { Logo } from '@/components/SiteLogo'
import { cookies } from 'next/headers'
import { IAccountResponse } from '@/apis/types'
import { Button } from '@/components/base/button'
import Link from 'next/link'
import { getTranslation } from '@/plugins/i18n'
export default async function Home() {
  const { t } = await getTranslation(['global'])
  let userInfo: IAccountResponse | undefined
  const session = (await cookies()).get('session')?.value
  if(session) {
    try {
      const { data } = await getAccountInfoApi()
      userInfo = data
    }
    catch (_error) {
      // ignore
    }
  }

  return (
    <main className="w-screen h-screen bg-background flex flex-col">
      <HomePageHeader />

      <div className="flex-1 flex flex-col justify-center items-center gap-8 px-4">
        <Logo className="h-[120px] w-[360px]" />

        <p className="text-muted-foreground text-center max-w-[600px] text-lg sm:text-xl">
          {t('global.home_description')}
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
