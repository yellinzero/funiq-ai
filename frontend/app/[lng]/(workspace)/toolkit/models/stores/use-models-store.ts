import type { IModelInfo, IProviderInfo } from '@/apis'
import { getModelsApi } from '@/apis/openapis/model-provider'
import { useQuery } from '@tanstack/react-query'
import { create } from 'zustand'

interface ModelsStoreState {
  models: Record<string, IModelInfo[]>
  currentProvider: IProviderInfo | null
  setModels: (provider: string, models: IModelInfo[]) => void
  setCurrentProvider: (provider: IProviderInfo | null) => void
}

export const useModelsStore = create<ModelsStoreState>(set => ({
  models: {},
  currentProvider: null,
  setModels: (provider, models) =>
    set(state => ({
      models: {
        ...state.models,
        [provider]: models,
      },
    })),
  setCurrentProvider: provider => set({ currentProvider: provider }),
}))

export function useModelsQuery(provider: string | null, lang: string) {
  const { setModels } = useModelsStore()

  return useQuery({
    queryKey: ['models', provider, lang],
    queryFn: async () => {
      if (!provider)
        return []
      const response = await getModelsApi(provider)
      const models = response.data?.models || []

      // Sort models: non-deprecated first, then deprecated
      const sortedModels = [...models].sort((a, b) => {
        if (a.deprecated === b.deprecated)
          return 0
        return a.deprecated ? 1 : -1
      })

      setModels(provider, sortedModels)
      return sortedModels
    },
    enabled: !!provider,
  })
}
