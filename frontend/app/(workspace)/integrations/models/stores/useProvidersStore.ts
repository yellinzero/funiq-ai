import { create } from 'zustand'
import { getModelProvidersApi } from '@/apis/openapis/model_providers'
import { components } from '@/types/openapi'
import { useQuery } from '@tanstack/react-query'

type ProviderInfo = components['schemas']['ProviderInfo']

interface ProvidersStoreState {
  providers: ProviderInfo[]
  error: Error | null
  setProviders: (providers: ProviderInfo[]) => void
  setError: (error: Error | null) => void
}

export const useProvidersStore = create<ProvidersStoreState>((set) => ({
  providers: [],
  error: null,
  setProviders: (providers) => set({ providers }),
  setError: (error) => set({ error }),
}))

export const useProvidersQuery = (lang: string) => {
  const { setProviders, setError } = useProvidersStore()

  return useQuery({
    queryKey: ['providers', lang],
    queryFn: async () => {
      try {
        const response = await getModelProvidersApi()
        const providers = response.data?.providers || []
        setProviders(providers)
        return providers
      } catch (error) {
        setError(error as Error)
        throw error
      }
    },
  })
}
