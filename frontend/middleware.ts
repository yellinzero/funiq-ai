import type { NextRequest } from 'next/server'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import acceptLanguage from 'accept-language'
import { fallbackLng, languages, I18N_COOKIE_NAME, headerName, normalizeLanguageCode, denormalizeLanguageCode } from './plugins/i18n/settings'

// Specify protected and public routes
const publicRoutes = [
  '/',
  '/forgot-password',
  '/sign-in',
  '/sign-up',
  '/create-tenant',
  '/activate',
]

const resolvedLanguages = languages.map(normalizeLanguageCode)
acceptLanguage.languages(resolvedLanguages)

export default async function middleware(req: NextRequest) {
  if (req.nextUrl.pathname.indexOf('icon') > -1 ||
      req.nextUrl.pathname.indexOf('chrome') > -1) {
    return NextResponse.next()
  }

  let lng
  if (req.cookies.has(I18N_COOKIE_NAME)) {
    lng = req.cookies.get(I18N_COOKIE_NAME)?.value || ''
  }
  if (!lng) {
    const acceptLang = acceptLanguage.get(req.headers.get('Accept-Language') || '')
    lng = acceptLang ? denormalizeLanguageCode(acceptLang) : fallbackLng
  }
  if (!lng) {
    lng = fallbackLng
  }

  const lngInPath = languages.find(loc => req.nextUrl.pathname.startsWith(`/${loc}`))
  const headers = new Headers(req.headers)
  headers.set(headerName, lngInPath || lng)

  const path = req.nextUrl.pathname
  const isPublicRoute = publicRoutes.includes(path)
  const session = (await cookies()).get('session')?.value

  if (!lngInPath && !req.nextUrl.pathname.startsWith('/_next')) {
    const newUrl = new URL(req.url)
    newUrl.pathname = `/${lng}${req.nextUrl.pathname}`

    return NextResponse.rewrite(newUrl, {
      headers: headers
    })
  }

  if (req.headers.has('referer')) {
    const refererUrl = new URL(req.headers.get('referer')!)
    const lngInReferer = languages.find((l) => refererUrl.pathname.startsWith(`/${l}`))
    const response = NextResponse.next({ headers })
    if (lngInReferer) {
      response.cookies.set(I18N_COOKIE_NAME, lngInReferer)
    }
    return response
  }

  if (!isPublicRoute && !session) {
    return NextResponse.redirect(new URL('/sign-in', req.url))
  }

  return NextResponse.next({ headers })
}

// Routes Middleware should not run on
export const config = {
  matcher: [
    `/((?!api|_next/static|_next/image|.*\\.png$|${languages.join('|')}).*)`,
  ],
}
