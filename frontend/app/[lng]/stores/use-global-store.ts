import {
  getAccountTenantsApi,
  getTenantUsersApi,
  getUserInfoApi,
  type ITenantResponse,
  type IUserInfo,
} from '@/apis'
import { useSessionCookie } from '@/hooks/use-session-cookie'
import { useQuery } from '@tanstack/react-query'
import { create } from 'zustand'

// State interfaces
interface GlobalState {
  // Current user
  currentUser: IUserInfo | null
  // Tenants list
  tenants: ITenantResponse[]
  // Users in current tenant
  tenantUsers: IUserInfo[]
  // Error states
  error: Error | null
  // Actions
  setCurrentUser: (user: IUserInfo | null) => void
  setTenants: (tenants: ITenantResponse[]) => void
  setTenantUsers: (users: IUserInfo[]) => void
  setError: (error: Error | null) => void
  getUserById: (userId: string) => IUserInfo | undefined
}

/**
 * Global store using Zustand
 * @client-only
 */
export const useGlobalStore = create<GlobalState>((set, get) => ({
  currentUser: null,
  tenants: [],
  tenantUsers: [],
  error: null,
  setCurrentUser: user => set({ currentUser: user }),
  setTenants: tenants => set({ tenants }),
  setTenantUsers: users => set({ tenantUsers: users }),
  setError: error => set({ error }),
  getUserById: (userId) => {
    return get().tenantUsers.find(user => user.id === userId)
  },
}))

/**
 * Hook for fetching current user data
 * @client-only
 */
export function useCurrentUserQuery() {
  const { setCurrentUser, setError } = useGlobalStore()

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      try {
        const response = await getUserInfoApi()
        const user = response.data ?? null
        setCurrentUser(user)
        return user
      }
      catch (error) {
        setError(error as Error)
        throw error
      }
    },
  })
}

/**
 * Hook for fetching tenants list
 * @client-only
 */
export function useTenantsQuery() {
  const { setTenants, setError } = useGlobalStore()

  return useQuery({
    queryKey: ['tenants'],
    queryFn: async () => {
      try {
        const response = await getAccountTenantsApi()
        const tenants = response.data ?? []
        setTenants(tenants)
        return tenants
      }
      catch (error) {
        setError(error as Error)
        throw error
      }
    },
  })
}

/**
 * Hook for fetching users in current tenant
 * @client-only
 */
export function useTenantUsersQuery() {
  const { setTenantUsers, setError } = useGlobalStore()
  const { getTenantId } = useSessionCookie()
  const tenantId = getTenantId()

  return useQuery({
    queryKey: ['tenantUsers', tenantId],
    queryFn: async () => {
      try {
        const response = await getTenantUsersApi(tenantId)
        const users = response.data ?? []
        setTenantUsers(users)
        return users
      }
      catch (error) {
        setError(error as Error)
        throw error
      }
    },
    enabled: !!tenantId, // Only run query if tenantId is provided
  })
}

// Selector hooks for convenient state access
export const useCurrentUser = () => useGlobalStore(state => state.currentUser)
export const useTenants = () => useGlobalStore(state => state.tenants)
export const useTenantUsers = () => useGlobalStore(state => state.tenantUsers)
export function useUserById(userId: string) {
  return useGlobalStore(state => state.getUserById(userId))
}
