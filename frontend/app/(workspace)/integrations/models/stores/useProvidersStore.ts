import { create } from 'zustand'
import { getModelProvidersApi } from '@/apis/openapis/model_providers'
import { useQuery } from '@tanstack/react-query'
import { IProviderInfo } from '@/apis/types'

interface ProvidersStoreState {
  providers: IProviderInfo[]
  error: Error | null
  setProviders: (providers: IProviderInfo[]) => void
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
