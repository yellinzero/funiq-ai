import { create } from 'zustand'
import { getProviderApi, saveProviderApi } from '@/apis/openapis/model_providers'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { type components } from '@/types/openapi'
import { HttpError, showErrorToast } from '@/apis/core'
import Toast from '@/components/Toast'

type ProviderResponse = components['schemas']['ProviderResponse']
type SaveProviderRequest = components['schemas']['SaveProviderRequest']

interface ProviderStoreState {
  provider: ProviderResponse | null
  error: Error | null
  setProvider: (provider: ProviderResponse | null) => void
  setError: (error: Error | null) => void
}

export const useProviderStore = create<ProviderStoreState>((set) => ({
  provider: null,
  error: null,
  setProvider: (provider) => set({
    provider
  }),
  setError: (error) => set({ error }),
}))

export const useProviderQuery = (providerName: string) => {
  const { setProvider, setError } = useProviderStore()

  return useQuery({
    queryKey: ['provider', providerName],
    queryFn: async () => {
      try {
        const response = await getProviderApi(providerName, {
          disableErrorToast: true,
        })
        const provider = response.data || null
        setProvider(provider)
        return provider
      } catch (error) {
        if (error instanceof HttpError && error.code !== 'M0001') {
          showErrorToast(error.code)
        }
        setError(error as Error)
        throw error
      }
    },
    enabled: !!providerName,
  })
}

export const useProviderMutation = (providerName: string) => {
  const queryClient = useQueryClient()
  const { setProvider, setError } = useProviderStore()

  return useMutation({
    mutationFn: async (data: SaveProviderRequest) => {
      const response = await saveProviderApi(providerName, data)
      return response.data
    },
    onSuccess: (data) => {
      setProvider(data || null)
      queryClient.invalidateQueries({ queryKey: ['provider', providerName] })
      queryClient.invalidateQueries({ queryKey: ['providers'] })
    },
    onError: (error: Error) => {
      setError(error)
    },
  })
}
