import { getAppApi, type IAppInfo, type IUpdateAppRequest, updateAppApi } from '@/apis'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { create } from 'zustand'

interface AppStoreState {
  app: IAppInfo | null
  setApp: (app: IAppInfo | null) => void
}

export const useAppStore = create<AppStoreState>(set => ({
  app: null,
  setApp: app => set({ app }),
}))

export function useAppQuery(appId: string) {
  const { setApp } = useAppStore()

  return useQuery({
    queryKey: ['app', appId],
    queryFn: async () => {
      const response = await getAppApi(appId)
      const app = response.data ?? null
      setApp(app)
      return app
    },
    enabled: !!appId,
  })
}

export function useUpdateAppMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ appId, data }: { appId: string, data: IUpdateAppRequest }) => {
      const response = await updateAppApi(appId, data)
      return response.data
    },
    onSuccess: (data) => {
      if (data) {
        queryClient.invalidateQueries({ queryKey: ['app', data.id] })
      }
    },
  })
}
