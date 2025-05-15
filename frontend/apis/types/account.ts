import type { components } from '@/types/openapi'

type IComponentsSchemas = components['schemas']

// Account related
export type IAccountStatus = IComponentsSchemas['AccountStatus']
export type IAccountTokenType = IComponentsSchemas['AccountTokenType']

// Account requests
export type IActivateAccountRequest = IComponentsSchemas['ActivateAccountRequest']
export type IActivateAccountVerifyRequest = IComponentsSchemas['ActivateAccountVerifyRequest']

// Account responses
export type IActivateAccountResponse = IComponentsSchemas['ActivateAccountResponse']
export type IActivateAccountVerifyResponse = IComponentsSchemas['ActivateAccountVerifyResponse']

// User related
export type IUserInfo = IComponentsSchemas['UserInfo']
export type IUserAddRequest = IComponentsSchemas['UserAddRequest']
export type IUserRoleUpdateRequest = IComponentsSchemas['UserRoleUpdateRequest']
export type IUpdateUserResponse = IComponentsSchemas['UpdateUserResponse']

// Tenant related
export type ITenantResponse = IComponentsSchemas['TenantResponse']
export type ITenantCreateRequest = IComponentsSchemas['TenantCreateRequest']
export type ITenantUpdateRequest = IComponentsSchemas['TenantUpdateRequest']
export type ITenantUserRole = IComponentsSchemas['TenantUserRole']
