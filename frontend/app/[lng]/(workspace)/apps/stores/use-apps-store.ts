import { createAppApi, deleteAppApi, getAppsApi, type IAppListResponse, type ICreateAppRequest, type IUpdateAppRequest, updateAppApi } from '@/apis'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { create } from 'zustand'

interface AppsStoreState {
  apps: IAppListResponse['apps']
  total: IAppListResponse['total']
  error: Error | null
  setApps: (apps: IAppListResponse['apps'], total: number) => void
  setError: (error: Error | null) => void
}

export const useAppsStore = create<AppsStoreState>(set => ({
  apps: [],
  total: 0,
  error: null,
  setApps: (apps, total) => set({ apps, total }),
  setError: error => set({ error }),
}))

export function useAppsQuery(page: number = 1, pageSize: number = 10, search?: string) {
  const { setApps, setError } = useAppsStore()

  return useQuery({
    queryKey: ['apps', page, pageSize, search],
    queryFn: async () => {
      try {
        const response = await getAppsApi({ page, page_size: pageSize, search })
        const { apps, total } = response.data || { apps: [], total: 0 }
        setApps(apps, total)
        return { apps, total }
      }
      catch (error) {
        setError(error as Error)
        throw error
      }
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

export function useUpdateAppMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ appId, data }: { appId: string, data: IUpdateAppRequest }) => {
      const response = await updateAppApi(appId, data)
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
