import type { getAppsUrl } from '@/apis/paths/app'
import type { ExtractParamsType } from '@/apis/types/helpers'
import type { components } from '@/types/openapi'

type IComponentsSchemas = components['schemas']
export type IGetAppsQuery = NonNullable<ExtractParamsType<'get', typeof getAppsUrl>>['query']
export type IAppInfo = IComponentsSchemas['AppInfo']
export type IAppListResponse = IComponentsSchemas['AppListResponse']
export type ICreateAppRequest = IComponentsSchemas['CreateAppRequest']
export type IUpdateAppRequest = IComponentsSchemas['UpdateAppRequest']
