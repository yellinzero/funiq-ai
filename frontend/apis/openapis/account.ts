import type { ITenantCreateRequest, ITenantUpdateRequest, IUserAddRequest, IUserRoleUpdateRequest } from '@/apis/types'
import { fetchApi } from '@/apis/core'
import {
  addTenantUserUrl,
  createTenantUrl,
  deleteTenantUrl,
  getAccountTenantsUrl,
  getTenantUsersUrl,
  getUserInfoUrl,
  removeTenantUserUrl,
  updateTenantUrl,
  updateUserRoleUrl,
} from '@/apis/paths'

export async function getUserInfoApi() {
  return await fetchApi.GET(getUserInfoUrl)
}

export async function getAccountTenantsApi() {
  return await fetchApi.GET(getAccountTenantsUrl)
}

export async function createTenantApi(body: ITenantCreateRequest) {
  return await fetchApi.POST(createTenantUrl, { body })
}

export async function updateTenantApi(tenantId: string, body: ITenantUpdateRequest) {
  return await fetchApi.PUT(updateTenantUrl, { params: { path: { tenant_id: tenantId } }, body })
}

export async function deleteTenantApi(tenantId: string) {
  return await fetchApi.DELETE(deleteTenantUrl, { params: { path: { tenant_id: tenantId } } })
}

export async function addTenantUserApi(tenantId: string, body: IUserAddRequest) {
  return await fetchApi.POST(addTenantUserUrl, { params: { path: { tenant_id: tenantId } }, body })
}

export async function updateUserRoleApi(tenantId: string, userId: string, body: IUserRoleUpdateRequest) {
  return await fetchApi.PUT(updateUserRoleUrl, { params: { path: { tenant_id: tenantId, user_id: userId } }, body })
}

export async function removeTenantUserApi(tenantId: string, userId: string) {
  return await fetchApi.DELETE(removeTenantUserUrl, { params: { path: { tenant_id: tenantId, user_id: userId } } })
}

export async function getTenantUsersApi(tenantId: string) {
  return await fetchApi.GET(getTenantUsersUrl, { params: { path: { tenant_id: tenantId } } })
}
