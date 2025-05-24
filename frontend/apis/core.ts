import type { CustomFetchResponse, ExtraConfig, HttpMethod } from '@/apis/types'
// TODO optimize typescript
import type { paths } from '@/types/openapi'
import { I18N_COOKIE_NAME } from '@/plugins/i18n/settings'
import { SESSION_COOKIE_NAME, TENANT_HEADER_NAME } from '@/utils/constants'
import i18next, { type TFunction } from 'i18next'
import createClient, {
  type Client,
  type ClientMethod,
  type InitParam,
  type MaybeOptionalInit,
  type Middleware,
} from 'openapi-fetch'
import { Cookies } from 'react-cookie'
import { toast } from 'sonner'

// API Clients
export const apiFetch = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE,
  credentials: 'include',
})
export const publicApiFetch = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE,
  credentials: 'include',
})

// Error Handling
interface ResponseData {
  code: string
  message: string
  data: unknown | null
}

export class HttpError extends Error {
  code: string
  status: number
  data: ResponseData | null
  response: Response

  constructor(msg: string, response: Response, data?: ResponseData) {
    super(msg)
    this.name = 'HttpError'
    this.code = data?.code || String(response.status)
    this.status = response.status
    this.data = data || null
    this.response = response
  }
}

// Add new utility function for cookie handling
async function getCookieContext() {
  if (typeof window === 'undefined') {
    // Server-side
    const { cookies: cookiesClient } = await import('next/headers')
    try {
      const cookieStore = await cookiesClient()
      const language = cookieStore.get(I18N_COOKIE_NAME)?.value ?? 'en'
      const session = JSON.parse(cookieStore.get(SESSION_COOKIE_NAME)?.value ?? '{}')
      return { language, session }
    }
    catch (error) {
      console.error('Failed to access server-side cookies:', error)
      return { language: 'en', session: {} }
    }
  }
  else {
    // Client-side
    const cookies = new Cookies()
    const language = cookies.get(I18N_COOKIE_NAME) ?? 'en'
    const session = cookies.get(SESSION_COOKIE_NAME) ?? {}
    return { language, session }
  }
}

// Middlewares
const requestContextMiddleware: Middleware = {
  async onRequest({ request }) {
    const { language, session } = await getCookieContext()

    request.headers.set(I18N_COOKIE_NAME, language)

    if (session.tenantId) {
      request.headers.set(TENANT_HEADER_NAME, session.tenantId)
    }
    if (session.accessToken) {
      request.headers.set('Authorization', `Bearer ${session.accessToken}`)
    }

    // FIXME: https://github.com/vercel/next.js/issues/63170
    if (typeof window === 'undefined') {
      const { cookies: cookiesClient } = await import('next/headers')
      const cookieStore = await cookiesClient()
      const cookie = cookieStore
        .getAll()
        .map(cookie => `${cookie.name}=${cookie.value}`)
        .join('; ')
      request.headers.set('Cookie', cookie)
    }
    return request
  },
}

const responseMiddleware: Middleware = {
  async onResponse({ response }) {
    const newAccessToken = response.headers.get('X-New-Access-Token')
    if (newAccessToken) {
      if (typeof window !== 'undefined') {
        const cookies = new Cookies()
        const session = cookies.get(SESSION_COOKIE_NAME) ?? {}
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)

        cookies.set(SESSION_COOKIE_NAME, { ...session, accessToken: newAccessToken }, {
          secure: true,
          sameSite: 'lax',
          expires: expiresAt,
          path: '/',
        })
      }
      else {
        // TODO: Server-side(if needed)
      }
    }

    return response
  },
  async onError({ error }) {
    console.error(error)
  },
}

// Apply middlewares
apiFetch.use(requestContextMiddleware)
apiFetch.use(responseMiddleware)

const defaultDisableErrorToastStatusList = [401] as number[]
const defaultDisableErrorToastCodeList = [] as string[]

export async function showErrorInfo(
  data: ResponseData | null,
  error: ResponseData | null,
  response: Response,
  t: TFunction,
  extraConfig?: ExtraConfig,
): Promise<boolean> {
  let disableToast = false
  if (extraConfig) {
    const { disableErrorToast, disableErrorToastStatusList, disableErrorToastCodeList } = extraConfig
    disableToast = !!(
      disableErrorToast
      || disableErrorToastStatusList?.includes(response.status)
      || disableErrorToastCodeList?.includes(data?.code || error?.code || '')
    )
  }

  const hasError = (data && data.code && data.code !== '0')
    || (error && error.code && error.code !== '0')
    || (response.status >= 400 && response.status < 600)

  if (!disableToast && hasError) {
    if ((data && data.code && data.code !== '0')
      || (error && error.code && error.code !== '0')) {
      toast.error(t(`error.${data?.code || error?.code}`) || t('error.undefined_error'))
    }
    else if (response.status >= 400 && response.status < 600) {
      toast.error(t(`error.http_status.${response.status}`))
    }
  }

  return hasError
}

export function createFetchApi(client: Client<paths>) {
  const handleResponse = async <Path extends keyof paths, Method extends HttpMethod>(
    // eslint-disable-next-line ts/no-empty-object-type
    promise: ReturnType<ClientMethod<{}, Method, Path>>,
    config?: ExtraConfig,
  ): Promise<CustomFetchResponse<Path, Method>> => {
    const { data, response, error } = await promise
    const { t } = i18next

    const mergedConfig = {
      ...config,
      disableErrorToastStatusList: [
        ...(config?.disableErrorToastStatusList || []),
        ...defaultDisableErrorToastStatusList,
      ],
      disableErrorToastCodeList: [
        ...(config?.disableErrorToastCodeList || []),
        ...defaultDisableErrorToastCodeList,
      ],
    }

    const hasError = await showErrorInfo(
      data as ResponseData,
      error as ResponseData,
      response,
      t,
      mergedConfig,
    )

    if (hasError) {
      const status = response.status
      if (status >= 400 && status < 600) {
        switch (status) {
          case 401: {
            if (typeof window !== 'undefined') {
              window.location.replace('/sign-in')
            }
            break
          }
          default: {
            break
          }
        }
      }
      throw new HttpError(
        data?.message || error?.message || response.statusText,
        response,
        data || error,
      )
    }

    return {
      data: data?.data,
      error: response.error,
      response: response.response,
    }
  }

  const createRequest = <T>(init?: T) => {
    return [...(init ? [init] : [])] as InitParam<T>
  }

  type MethodConfig<M extends HttpMethod> = {
    [P in keyof paths as paths[P] extends { [K in M]: unknown } ? P : never]: {
      path: P
      init?: MaybeOptionalInit<paths[P], M>
    }
  }

  const createMethod = <M extends HttpMethod>(method: M) => {
    return <P extends keyof MethodConfig<M>>(
      url: P,
      init?: MethodConfig<M>[P]['init'],
      config?: ExtraConfig,
    ) => handleResponse<P, M>(
      (client[method.toUpperCase() as Uppercase<M>] as any)(url, ...createRequest(init)),
      config,
    )
  }

  return {
    GET: createMethod('get'),
    POST: createMethod('post'),
    PUT: createMethod('put'),
    DELETE: createMethod('delete'),
    OPTIONS: createMethod('options'),
    HEAD: createMethod('head'),
    PATCH: createMethod('patch'),
    TRACE: createMethod('trace'),
  }
}

export const fetchApi = createFetchApi(apiFetch)
