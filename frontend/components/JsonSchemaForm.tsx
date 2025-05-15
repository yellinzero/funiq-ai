import type FormType from '@rjsf/core'
import type { FormProps } from '@rjsf/core'
import type { Localize } from 'ajv-i18n/localize/types'
import { fallbackLng, type Locale } from '@/plugins/i18n/settings'
import Form from '@rjsf/shadcn'
import { customizeValidator } from '@rjsf/validator-ajv8'
import ajvLocalizer from 'ajv-i18n'

export interface JsonSchemaFormProps extends FormProps {
  hideSubmitButton?: boolean
  locale?: Locale
  ref?: React.Ref<FormType>
}

const localizer: Record<Locale, Localize> = {
  en: ajvLocalizer.en,
  zh_CN: ajvLocalizer.zh,
}

export default function JsonSchemaForm(props: Omit<JsonSchemaFormProps, 'validator'>) {
  const { ref, locale, noHtml5Validate, showErrorList, hideSubmitButton, children, ...rest } = props
  const resolvedLocale = locale ?? fallbackLng
  const validator = customizeValidator({}, localizer[resolvedLocale])
  const resolvedNoHtml5Validate = noHtml5Validate ?? true
  const resolvedShowErrorList = showErrorList ?? false
  const resolvedHideSubmitButton = hideSubmitButton ?? true
  return (
    <Form
      {...rest}
      ref={ref}
      validator={validator}
      showErrorList={resolvedShowErrorList}
      noHtml5Validate={resolvedNoHtml5Validate}
    >
      {resolvedHideSubmitButton && !children ? null : children}
    </Form>
  )
}
