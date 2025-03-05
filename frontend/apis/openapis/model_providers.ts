import { ExtraConfig, type ExtractBodyType, fetchApi } from '@/apis/core'
import {
  getModelProvidersUrl,
  getModelsUrl,
  getProviderUrl,
  saveProviderUrl,
  getModelUrl,
  saveModelUrl,
  enableModelUrl,
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

export async function getModelApi(providerName: string, modelName: string) {
  return await fetchApi.GET(getModelUrl, {
    params: {
      path: {
        provider_name: providerName,
        model_name: modelName,
      },
    },
  })
}

export async function saveModelApi(
  providerName: string,
  modelName: string,
  body: ExtractBodyType<'post', typeof saveModelUrl>,
) {
  return await fetchApi.POST(saveModelUrl, {
    params: {
      path: {
        provider_name: providerName,
        model_name: modelName,
      },
    },
    body,
  })
}

export async function enableModelApi(providerName: string, modelName: string) {
  return await fetchApi.POST(enableModelUrl, {
    params: {
      path: {
        provider_name: providerName,
        model_name: modelName,
      },
    },
  })
}


