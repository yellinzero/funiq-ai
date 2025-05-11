// TODO optimize typescript
import type { paths } from '@/types/openapi'
import type {
  Client,
  ClientMethod,
  FetchResponse,
  InitParam,
  MaybeOptionalInit,
  Middleware,
} from 'openapi-fetch'
import { toast } from 'sonner'
import { I18N_COOKIE_NAME } from '@/plugins/i18n/settings'
import { SESSION_COOKIE_NAME, TENANT_HEADER_NAME } from '@/utils/constants'
import createClient from 'openapi-fetch'
import { Cookies } from 'react-cookie'
import { redirect } from 'next/navigation'
import i18next, { TFunction } from 'i18next'


// Types
export type HttpMethod = 'get' | 'put' | 'post' | 'delete' | 'options' | 'head' | 'patch' | 'trace'

export type ExtractInitType<Method extends HttpMethod, Path extends keyof paths> =
  MaybeOptionalInit<paths[Path], Method>

export type ExtractBodyType<Method extends HttpMethod, Path extends keyof paths> =
  'body' extends keyof MaybeOptionalInit<paths[Path], Method>
  ? MaybeOptionalInit<paths[Path], Method>['body']
  : never

export type ExtractParamsType<Method extends HttpMethod, Path extends keyof paths> =
  'params' extends keyof MaybeOptionalInit<paths[Path], Method>
  ? MaybeOptionalInit<paths[Path], Method>['params']
  : never

export type PathsWithMethod<T, M extends HttpMethod> = keyof {
  [P in keyof T as T[P] extends { [K in M]: unknown } ? P : never]: T[P]
}

export type ExtractResponseType<Method extends HttpMethod, Path extends keyof paths> =
  paths[Path][Method] extends { responses: { 200: { content: { 'application/json': infer R } } } }
  ? R extends { data: infer D }
  ? D
  : never
  : never

export type CustomFetchResponse<Path extends keyof paths, Method extends HttpMethod> =
  | {
    data: ExtractResponseType<Method, Path>
    error?: never
    response: FetchResponse<paths[Path], MaybeOptionalInit<paths[Path], Method>, Path>['response']
  }
  | {
    data?: never
    error: FetchResponse<paths[Path], MaybeOptionalInit<paths[Path], Method>, Path>['error']
    response: FetchResponse<paths[Path], MaybeOptionalInit<paths[Path], Method>, Path>['response']
  }


export interface ExtraConfig {
  disableErrorToast?: boolean
  disableErrorToastStatusList?: number[]
  disableErrorToastCodeList?: string[]
}

// Constants
const namespaces = ['error']

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
        cookies.set(SESSION_COOKIE_NAME, { ...session, accessToken: newAccessToken })
      }
      else {
        // TODO: Server-side(if needed)
        // const { cookies } = await import('next/headers')
        // const cookieStore = await cookies()
        // const session = JSON.parse(cookieStore.get(SESSION_COOKIE_NAME)?.value ?? '{}')
        // cookieStore.set(SESSION_COOKIE_NAME, JSON.stringify({ ...session, accessToken: newAccessToken }))
      }
    }

    const status = response.status
    if (status >= 400 && status < 600) {
      switch (status) {
        case 401: {
          redirect('/sign-in')
          break
        }
        default: {
          break
        }
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
      path: P;
      init?: MaybeOptionalInit<paths[P], M>;
    }
  }

  const createMethod = <M extends HttpMethod>(method: M) => {
    return <P extends keyof MethodConfig<M>>(
      url: P,
      init?: MethodConfig<M>[P]['init'],
      config?: ExtraConfig
    ) => handleResponse<P, M>(
      (client[method.toUpperCase() as Uppercase<M>] as any)(url, ...createRequest(init)),
      config
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
