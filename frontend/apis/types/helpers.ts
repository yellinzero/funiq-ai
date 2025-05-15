import type { paths } from '@/types/openapi'
// type utils
import type { FetchResponse, MaybeOptionalInit } from 'openapi-fetch'
import type { HttpMethod } from './base'

// Types

export type ExtractInitType<Method extends HttpMethod, Path extends keyof paths> =
  NonNullable<MaybeOptionalInit<paths[Path], Method>>

export type ExtractBodyType<Method extends HttpMethod, Path extends keyof paths> =
  'body' extends keyof ExtractInitType<Method, Path>
    ? ExtractInitType<Method, Path>['body']
    : never

export type ExtractParamsType<Method extends HttpMethod, Path extends keyof paths> =
  'params' extends keyof ExtractInitType<Method, Path>
    ? ExtractInitType<Method, Path>['params']
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
