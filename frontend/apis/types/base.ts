export type HttpMethod = 'get' | 'put' | 'post' | 'delete' | 'options' | 'head' | 'patch' | 'trace'

export interface ExtraConfig {
  disableErrorToast?: boolean
  disableErrorToastStatusList?: number[]
  disableErrorToastCodeList?: string[]
}
