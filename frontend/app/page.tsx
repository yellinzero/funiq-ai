import { getAccountInfoApi } from '@/apis/openapis/account'
import CurrentUserInfoBox from '@/components/CurrentUserInfoBox'
import HomePageHeader from '@/components/HomePageHeader'
import { LogoWithName } from '@/components/SiteLogo'
import { initTranslations } from '@/plugins/i18n'
import { getLocaleFromServer } from '@/plugins/i18n/server'
import { Box, Button, Link, Typography } from '@mui/material'
import { cookies } from 'next/headers'
import { IAccountResponse } from '@/apis/types'

export default async function Home() {
  const locale = await getLocaleFromServer()
  const { t } = await initTranslations(locale, ['global'])
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
    <Box sx={{
      width: '100vw',
      height: '100vh',
      backgroundColor: 'background.default',
      display: 'flex',
      flexDirection: 'column',
    }}
    >
      <HomePageHeader />
      <Box sx={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 4,
        px: 2,
      }}
      >
        <LogoWithName height={120} />
        <Typography
          variant="h5"
          color="text.secondary"
          align="center"
          sx={{
            maxWidth: '600px',
            fontSize: {
              xs: '1.1rem',
              sm: '1.3rem',
            },
          }}
        >
          {t('home_description', { ns: 'global' })}
        </Typography>
        {userInfo && <Link href="/chat" underline="none"><CurrentUserInfoBox userInfo={userInfo} showName /></Link>}
        {!userInfo && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, alignItems: 'center' }}>
            <Link href="/sign-in" underline="hover">
              <Button
                variant="contained"
                color="primary"
                size="large"
                sx={{
                  px: 4,
                  py: 1,
                  borderRadius: 2,
                  fontSize: '1.1rem',
                }}
              >
                {t('sign_in', { ns: 'global' })}
              </Button>
            </Link>
            <Link href="/sign-up" underline="hover">
              <Button
                variant="text"
              >
                {t('sign_up', { ns: 'global' })}
              </Button>
            </Link>
          </Box>
        )}
      </Box>
    </Box>
  )
}
