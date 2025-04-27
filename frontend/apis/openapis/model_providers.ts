import { ExtraConfig, type ExtractBodyType, fetchApi } from '@/apis/core'
import {
  getModelProvidersUrl,
  getModelsUrl,
  getProviderUrl,
  saveProviderUrl,
} from '@/apis/paths/model_providers'

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

export async function getProviderApi(providerName: string, config?: ExtraConfig) {
  return await fetchApi.GET(getProviderUrl, {
    params: {
      path: {
        provider_name: providerName,
      },
    },
  }, config)
}

export async function saveProviderApi(
  providerName: string,
  body: ExtractBodyType<'post', typeof saveProviderUrl>,
) {
  return await fetchApi.POST(saveProviderUrl, {
    params: {
      path: {
        provider_name: providerName,
      },
    },
    body,
  })
}