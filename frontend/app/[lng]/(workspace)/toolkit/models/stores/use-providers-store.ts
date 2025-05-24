import type { IProviderInfo } from '@/apis'
import { getModelProvidersApi } from '@/apis/openapis/model-provider'
import { useQuery } from '@tanstack/react-query'
import { create } from 'zustand'

interface ProvidersStoreState {
  providers: IProviderInfo[]
  setProviders: (providers: IProviderInfo[]) => void
}

export const useProvidersStore = create<ProvidersStoreState>(set => ({
  providers: [],
  setProviders: providers => set({ providers }),
}))

export function useProvidersQuery(lang: string) {
  const { setProviders } = useProvidersStore()

  return useQuery({
    queryKey: ['providers', lang],
    queryFn: async () => {
      const response = await getModelProvidersApi()
      const providers = response.data?.providers || []
      setProviders(providers)
      return providers
    },
  })
}
