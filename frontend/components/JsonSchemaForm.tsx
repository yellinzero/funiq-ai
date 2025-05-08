import Form from '@rjsf/shadcn';
import { FormProps } from '@rjsf/core';
import type FormType from '@rjsf/core';
import { forwardRef } from 'react';
import {customizeValidator} from '@rjsf/validator-ajv8';
import ajvLocalizer from 'ajv-i18n';
import { Locale, fallbackLang } from '@/plugins/i18n/settings';
import { Localize } from 'ajv-i18n/localize/types';
export interface JsonSchemaFormProps extends FormProps {
  hideSubmitButton?: boolean
  locale?: Locale
  ref?: React.Ref<FormType>
}

const localizer: Record<Locale, Localize> = {
  en: ajvLocalizer.en,
  'zh_CN': ajvLocalizer.zh
}


export default function JsonSchemaForm(props: Omit<JsonSchemaFormProps, 'validator'>) {
  const { ref, ...rest } = props
  const locale = props.locale ?? fallbackLang
  const noHtml5Validate = props.noHtml5Validate ?? true
  const showErrorList = props.showErrorList ?? false
  const validator = customizeValidator({}, localizer[locale])
  const hideSubmitButton = props.hideSubmitButton ?? true
  return (
    <Form
      {...rest}
      ref={ref}
      validator={validator}
      showErrorList={showErrorList}
      noHtml5Validate={noHtml5Validate}
      // hide default submit button
      children={hideSubmitButton && !props.children ? <></> : props.children}
    />
  )
}
