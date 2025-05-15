import i18next from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import resourcesToBackend from 'i18next-resources-to-backend'
import { initReactI18next } from 'react-i18next/initReactI18next'
import { defaultNS, denormalizeLanguageCode, fallbackLng, I18N_COOKIE_NAME, languages } from './settings'

const runsOnServerSide = typeof window === 'undefined'

i18next
  .use(initReactI18next)
  .use(LanguageDetector)
  .use(resourcesToBackend((language: string, namespace: string) => import(`@/locales/${language}/${namespace}.json`)))
  .init({
    supportedLngs: languages,
    fallbackLng,
    lng: undefined, // let detect the language on client side
    fallbackNS: defaultNS,
    defaultNS,
    detection: {
      lookupQuerystring: 'lng',
      lookupCookie: I18N_COOKIE_NAME,
      lookupLocalStorage: I18N_COOKIE_NAME,
      lookupSessionStorage: I18N_COOKIE_NAME,
      order: ['cookie', 'path', 'htmlTag', 'navigator'],
      convertDetectedLanguage: lng => denormalizeLanguageCode(lng),
    },
    preload: runsOnServerSide ? languages : [],
    nsSeparator: '.',
    interpolation: {
      escapeValue: false,
    },
  })

export default i18next
