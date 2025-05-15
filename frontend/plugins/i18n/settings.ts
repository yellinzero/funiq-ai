export const I18N_COOKIE_NAME = 'X-LANGUAGE'
export const fallbackLng = 'en'
export const languages = [fallbackLng, 'zh_CN']
export const defaultNS = ['global', 'error']
export const headerName = 'x-i18next-current-language'

export type Locale = typeof languages[number]

export const languagesOptions = [{
  value: 'en',
  label: 'English',
}, {
  value: 'zh_CN',
  label: '简体中文',
}]

export function normalizeLanguageCode(lang: string) {
  return lang.replace('_', '-')
}

export function denormalizeLanguageCode(lang: string) {
  return lang.replace('-', '_')
}
