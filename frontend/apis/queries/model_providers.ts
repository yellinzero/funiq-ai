import { getModelProvidersApi, getModelsApi } from '@/apis/openapis/model_providers'
import { queryOptions } from '@tanstack/react-query'


export function getModelsProvidersOptions(lang: string) {
  return queryOptions({
    queryKey: ['models-providers', lang],
    queryFn: getModelProvidersApi,
  })
}

export const modelsQueryKey = (providerName: string, lang: string) => ['models', providerName, lang] as const
export const getModelsOptions = (providerName: string, lang: string) => queryOptions({
  queryKey: modelsQueryKey(providerName, lang),
  queryFn: () => getModelsApi(providerName),
})


