import { components } from '@/types/openapi'

export type IComponentsSchemas = components['schemas']
export type IModelInfo = IComponentsSchemas['ModelInfo']
export type IProviderInfo = IComponentsSchemas['ProviderInfo']
export type IAccountResponse = IComponentsSchemas['AccountResponse']
