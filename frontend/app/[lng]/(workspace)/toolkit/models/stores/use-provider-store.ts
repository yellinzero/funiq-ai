import type { components } from '@/types/openapi'
import { getProviderApi, saveProviderApi } from '@/apis/openapis/model-provider'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { create } from 'zustand'

type ProviderResponse = components['schemas']['ProviderResponse']
type SaveProviderRequest = components['schemas']['SaveProviderRequest']

interface ProviderStoreState {
  provider: ProviderResponse | null
  error: Error | null
  setProvider: (provider: ProviderResponse | null) => void
  setError: (error: Error | null) => void
}

export const useProviderStore = create<ProviderStoreState>(set => ({
  provider: null,
  error: null,
  setProvider: provider => set({
    provider,
  }),
  setError: error => set({ error }),
}))

export function useProviderQuery(providerName: string) {
  const { setProvider, setError } = useProviderStore()

  return useQuery({
    queryKey: ['provider', providerName],
    queryFn: async () => {
      try {
        const response = await getProviderApi(providerName, {
          disableErrorToastCodeList: ['C0301'],
        })
        const provider = response.data || null
        setProvider(provider)
        return provider
      }
      catch (error) {
        setError(error as Error)
        throw error
      }
    },
    enabled: !!providerName,
  })
}

export function useProviderMutation(providerName: string) {
  const queryClient = useQueryClient()
  const { setProvider, setError } = useProviderStore()

  return useMutation({
    mutationFn: async (data: SaveProviderRequest) => {
      try {
        const response = await saveProviderApi(providerName, data)
        return response.data
      }
      catch (error) {
        console.error(error)
        throw error
      }
    },
    onSuccess: (data) => {
      setProvider(data || null)
      queryClient.invalidateQueries({ queryKey: ['provider', providerName] })
      queryClient.invalidateQueries({ queryKey: ['providers'] })
    },
    onError: (error: Error) => {
      setError(error)
      throw error
    },
  })
}
