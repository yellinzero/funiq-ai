import type { IProviderInfo } from '@/apis'
import { getModelProvidersApi } from '@/apis/openapis/model-provider'
import { useQuery } from '@tanstack/react-query'
import { create } from 'zustand'

interface ProvidersStoreState {
  providers: IProviderInfo[]
  error: Error | null
  setProviders: (providers: IProviderInfo[]) => void
  setError: (error: Error | null) => void
}

export const useProvidersStore = create<ProvidersStoreState>(set => ({
  providers: [],
  error: null,
  setProviders: providers => set({ providers }),
  setError: error => set({ error }),
}))

export function useProvidersQuery(lang: string) {
  const { setProviders, setError } = useProvidersStore()

  return useQuery({
    queryKey: ['providers', lang],
    queryFn: async () => {
      try {
        const response = await getModelProvidersApi()
        const providers = response.data?.providers || []
        setProviders(providers)
        return providers
      }
      catch (error) {
        setError(error as Error)
        throw error
      }
    },
  })
}
