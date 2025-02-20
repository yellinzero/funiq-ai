import Form from '@rjsf/mui';
import { FormProps } from '@rjsf/core';
import type FormType from '@rjsf/core';
import { forwardRef } from 'react';

export interface JsonSchemaFormProps extends FormProps {
  hideSubmitButton?: boolean
}
const JsonSchemaForm = forwardRef<FormType, JsonSchemaFormProps>((props, ref) => {
  const hideSubmitButton = props.hideSubmitButton ?? true
  return (
    <Form
      {...props}
      ref={ref}
      // hide default submit button
      children={hideSubmitButton && !props.children ? <></> : props.children}
    />
  )
});

export default JsonSchemaForm;
