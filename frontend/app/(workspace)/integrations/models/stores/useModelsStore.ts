import { create } from 'zustand'
import { getModelsApi } from '@/apis/openapis/model_providers'
import { components } from '@/types/openapi'
import { useQuery } from '@tanstack/react-query'

type AIModelEntity = components['schemas']['AIModelEntity']
type ProviderInfo = components['schemas']['ProviderInfo']

interface ModelsStoreState {
  models: Record<string, AIModelEntity[]>
  currentProvider: ProviderInfo | null
  error: Error | null
  setModels: (provider: string, models: AIModelEntity[]) => void
  setCurrentProvider: (provider: ProviderInfo | null) => void
  setError: (error: Error | null) => void
}

export const useModelsStore = create<ModelsStoreState>((set) => ({
  models: {},
  currentProvider: null,
  error: null,
  setModels: (provider, models) =>
    set((state) => ({
      models: {
        ...state.models,
        [provider]: models,
      },
    })),
  setCurrentProvider: (provider) => set({ currentProvider: provider }),
  setError: (error) => set({ error }),
}))

export const useModelsQuery = (provider: string | null, lang: string) => {
  const { setModels, setError } = useModelsStore()

  return useQuery({
    queryKey: ['models', provider, lang],
    queryFn: async () => {
      if (!provider) return []
      try {
        const response = await getModelsApi(provider)
        const models = response.data?.models || []

        // Sort models: non-deprecated first, then deprecated
        const sortedModels = [...models].sort((a, b) => {
          if (a.deprecated === b.deprecated) return 0
          return a.deprecated ? 1 : -1
        })

        setModels(provider, sortedModels)
        return sortedModels
      } catch (error) {
        setError(error as Error)
        throw error
      }
    },
    enabled: !!provider,
  })
}
