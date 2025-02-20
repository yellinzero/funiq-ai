import { fetchApi } from '@/apis/core'
import { getModelProvidersUrl, getModelsUrl } from '@/apis/paths/model_providers'

export async function getModelProvidersApi() {
  return await fetchApi.GET(getModelProvidersUrl)
}

export async function getModelsApi(providerName: string) {
  return await fetchApi.GET(getModelsUrl, {
    params: {
      path: {
        provider_name: providerName,
      },
    },
  })
}
