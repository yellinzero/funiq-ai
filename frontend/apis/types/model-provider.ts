import type { components } from '@/types/openapi'

type IComponentsSchemas = components['schemas']

// Model related
export type IModelType = IComponentsSchemas['ModelType']
export type IModelInfo = IComponentsSchemas['ModelInfo']
export type IModelFeature = IComponentsSchemas['ModelFeature']
export type IModelPropertyKey = IComponentsSchemas['ModelPropertyKey']
export type IModelParameterRulesSchema = IComponentsSchemas['ModelParameterRulesSchema']
export type IAIModelEntity = IComponentsSchemas['AIModelEntity']

// Provider related
export type IProviderInfo = IComponentsSchemas['ProviderInfo']
export type IProviderDoc = IComponentsSchemas['ProviderDoc']
export type IProviderConfigSchema = IComponentsSchemas['ProviderConfigSchema']
export type IProviderResponse = IComponentsSchemas['ProviderResponse']
export type ISaveProviderRequest = IComponentsSchemas['SaveProviderRequest']

// Active provider related
export type IActiveModelProviderModelItem = IComponentsSchemas['ActiveModelProviderModelItem']
export type IActiveModelProviderWithModels = IComponentsSchemas['ActiveModelProviderWithModels']

// Response types
export type IGetModelProvidersResponse = IComponentsSchemas['GetModelProvidersResponse']
export type IGetModelsResponse = IComponentsSchemas['GetModelsResponse']

// Pricing related
export type IPriceConfig = IComponentsSchemas['PriceConfig']
