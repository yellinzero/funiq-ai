import { createAppApi, deleteAppApi, getAppsApi, type IAppListResponse, type ICreateAppRequest } from '@/apis'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { create } from 'zustand'

interface AppsStoreState {
  apps: IAppListResponse['apps']
  total: IAppListResponse['total']
  setApps: (apps: IAppListResponse['apps'], total: number) => void
}

export const useAppsStore = create<AppsStoreState>(set => ({
  apps: [],
  total: 0,
  setApps: (apps, total) => set({ apps, total }),
}))

export function useAppsQuery(page: number = 1, pageSize: number = 10, search?: string) {
  const { setApps } = useAppsStore()

  return useQuery({
    queryKey: ['apps', page, pageSize, search],
    queryFn: async () => {
      const response = await getAppsApi({ page, page_size: pageSize, search })
      const { apps, total } = response.data || { apps: [], total: 0 }
      setApps(apps, total)
      return { apps, total }
    },
  })
}

export function useCreateAppMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ICreateAppRequest) => {
      const response = await createAppApi(data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apps'] })
    },
  })
}

export function useDeleteAppMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (appId: string) => {
      const response = await deleteAppApi(appId)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apps'] })
    },
  })
}
