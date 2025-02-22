import Form from '@rjsf/mui';
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
}

const localizer: Record<Locale, Localize> = {
  en: ajvLocalizer.en,
  'zh_CN': ajvLocalizer.zh
}

const JsonSchemaForm = forwardRef<FormType, Omit<JsonSchemaFormProps, 'validator'>>((props, ref) => {
  const locale = props.locale ?? fallbackLang
  const noHtml5Validate = props.noHtml5Validate ?? true
  const showErrorList = props.showErrorList ?? false
  const validator = customizeValidator({}, localizer[locale])
  const hideSubmitButton = props.hideSubmitButton ?? true
  return (
    <Form
      {...props}
      ref={ref}
      validator={validator}
      showErrorList={showErrorList}
      noHtml5Validate={noHtml5Validate}
      // hide default submit button
      children={hideSubmitButton && !props.children ? <></> : props.children}
    />
  )
});

export default JsonSchemaForm;
