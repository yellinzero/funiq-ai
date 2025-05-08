export const fallbackLang = 'en'
export const languages = [fallbackLang, 'zh_CN']
export const I18N_COOKIE_NAME = 'X-LANGUAGE'
export const defaultNS = 'global'

export function getOptions(lang = fallbackLang, ns = defaultNS) {
  return {
    // debug: true,
    supportedLangs: languages,
    fallbackLang,
    lng: lang,
    fallbackNS: defaultNS,
    defaultNS,
    nsSeparator: '.',
    ns,
  }
}

export type Locale = typeof languages[number]

export const languagesOptions = [{
  value: 'en',
  label: 'English',
}, {
  value: 'zh_CN',
  label: '简体中文',
}]
