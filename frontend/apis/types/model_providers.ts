import type { ExtractResponseType } from '@/apis/core'
import type { getModelProvidersUrl, getModelsUrl } from '@/apis/paths/model_providers'

export type IGetModelProvidersResponse = ExtractResponseType<'get', typeof getModelProvidersUrl>
export type IGetModelsResponse = ExtractResponseType<'get', typeof getModelsUrl>
