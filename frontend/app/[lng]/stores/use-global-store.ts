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
  // Actions
  setCurrentUser: (user: IUserInfo | null) => void
  setTenants: (tenants: ITenantResponse[]) => void
  setTenantUsers: (users: IUserInfo[]) => void
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
  setCurrentUser: user => set({ currentUser: user }),
  setTenants: tenants => set({ tenants }),
  setTenantUsers: users => set({ tenantUsers: users }),
  getUserById: (userId) => {
    return get().tenantUsers.find(user => user.id === userId)
  },
}))

/**
 * Hook for fetching current user data
 * @client-only
 */
export function useCurrentUserQuery() {
  const { setCurrentUser } = useGlobalStore()

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await getUserInfoApi()
      const user = response.data ?? null
      setCurrentUser(user)
      return user
    },
  })
}

/**
 * Hook for fetching tenants list
 * @client-only
 */
export function useTenantsQuery() {
  const { setTenants } = useGlobalStore()

  return useQuery({
    queryKey: ['tenants'],
    queryFn: async () => {
      const response = await getAccountTenantsApi()
      const tenants = response.data ?? []
      setTenants(tenants)
      return tenants
    },
  })
}

/**
 * Hook for fetching users in current tenant
 * @client-only
 */
export function useTenantUsersQuery() {
  const { setTenantUsers } = useGlobalStore()
  const { getTenantId } = useSessionCookie()
  const tenantId = getTenantId()

  return useQuery({
    queryKey: ['tenantUsers', tenantId],
    queryFn: async () => {
      const response = await getTenantUsersApi(tenantId)
      const users = response.data ?? []
      setTenantUsers(users)
      return users
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
