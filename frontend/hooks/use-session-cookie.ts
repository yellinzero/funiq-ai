import { SESSION_COOKIE_NAME } from '@/utils/constants'
import { useCookies } from 'react-cookie'

export function useSessionCookie() {
  const [cookies, setCookies, removeCookie] = useCookies()
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)

  function setAuth(accessToken: string, tenantId?: string) {
    setCookies(SESSION_COOKIE_NAME, {
      accessToken,
      tenantId,
    }, {
      secure: true,
      sameSite: 'lax',
      expires: expiresAt,
      path: '/',
    })
  }

  function updateTenantId(tenantId: string) {
    const currentSession = cookies[SESSION_COOKIE_NAME]
    if (!currentSession) return

    setCookies(SESSION_COOKIE_NAME, {
      ...currentSession,
      tenantId,
    }, {
      secure: true,
      sameSite: 'lax',
      expires: expiresAt,
      path: '/',
    })
  }

  function getAuth() {
    const session = cookies[SESSION_COOKIE_NAME]
    return {
      accessToken: session?.accessToken,
      tenantId: session?.tenantId,
    }
  }

  function clearAuth() {
    removeCookie(SESSION_COOKIE_NAME)
  }

  return {
    setAuth,
    getAuth,
    clearAuth,
    updateTenantId,
  }
}
