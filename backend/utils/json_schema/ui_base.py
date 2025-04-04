# Type for react json schema
# not fully covered, just for necessary fields
# some FE fields types are not included, like ComponentType for ui:field, TemplatesType, and so on
from typing import Any

from pydantic import BaseModel, Field

from utils.common.i18n import TranslatableText


class GlobalUISchemaOptions(BaseModel):
    """Global UI schema options that can be set globally and used as fallbacks when no field-level value is provided"""

    addable: bool | None = Field(
        None, alias="addable", description="If false, new items cannot be added to array fields"
    )
    copyable: bool | None = Field(None, alias="copyable", description="If true, array items can be copied")
    orderable: bool | None = Field(None, alias="orderable", description="If false, array items cannot be ordered")
    removable: bool | None = Field(None, alias="removable", description="If false, array items will not be removable")
    label: bool | None = Field(None, alias="label", description="If false, field labels will be omitted")
    duplicate_key_suffix_separator: str | None = Field(
        None,
        alias="duplicateKeySuffixSeparator",
        description="Separator between key name and integer for duplicate additionalProperties keys",
    )

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        alias_generator = None


class UISchemaSubmitButtonOptions(BaseModel):
    """Options for customizing the submit button behavior"""

    submit_text: str | TranslatableText | None = Field(
        None, alias="submitText", description="Text to display on submit button"
    )
    norender: bool | None = Field(None, alias="norender", description="If true, removes submit button completely")
    props: dict | None = Field(None, alias="props", description="Additional props to pass to submit button")

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        alias_generator = None


class UIOptionsBaseTypeWithPrefix(BaseModel):
    """Base type for UI options with ui: prefix. Contains all possible UI customization options."""

    # Global options
    ui_addable: bool | None = Field(None, alias="ui:addable")
    ui_copyable: bool | None = Field(None, alias="ui:copyable")
    ui_orderable: bool | None = Field(None, alias="ui:orderable")
    ui_removable: bool | None = Field(None, alias="ui:removable")
    ui_label: bool | None = Field(None, alias="ui:label")
    ui_duplicate_key_suffix_separator: str | None = Field(None, alias="ui:duplicateKeySuffixSeparator")

    # Styling options
    ui_class_names: str | None = Field(None, alias="ui:classNames", description="CSS class names to apply to field")
    ui_style: dict | None = Field(None, alias="ui:style", description="Custom styles to apply to field")

    # Display options
    ui_title: str | TranslatableText | None = Field(None, alias="ui:title", description="Custom title for the field")
    ui_description: str | TranslatableText | None = Field(
        None, alias="ui:description", description="Custom description for the field"
    )
    ui_placeholder: str | TranslatableText | None = Field(
        None, alias="ui:placeholder", description="Placeholder text for inputs"
    )
    ui_help: str | TranslatableText | None = Field(None, alias="ui:help", description="Help text shown next to field")

    # Input behavior options
    ui_autofocus: bool | None = Field(None, alias="ui:autofocus", description="If true, field will be focused on load")
    ui_autocomplete: str | None = Field(None, alias="ui:autocomplete", description="HTML autocomplete attribute")
    ui_disabled: bool | None = Field(None, alias="ui:disabled", description="If true, field will be disabled")
    ui_empty_value: Any | None = Field(None, alias="ui:emptyValue", description="Value to use when input is empty")
    ui_enum_disabled: list[str | int | bool] | None = Field(
        None, alias="ui:enumDisabled", description="List of enum values to disable"
    )
    ui_hide_error: bool | None = Field(None, alias="ui:hideError", description="If true, hide error display for field")
    ui_readonly: bool | None = Field(None, alias="ui:readonly", description="If true, field will be read-only")

    # Layout options
    ui_order: list[str] | None = Field(None, alias="ui:order", description="Custom ordering of object properties")
    ui_inline: bool | None = Field(None, alias="ui:inline", description="If true, checkboxes render inline")

    # Widget options
    ui_widget: str | None = Field(None, alias="ui:widget", description="Custom widget to use for field")
    ui_input_type: str | None = Field(None, alias="ui:inputType", description="HTML input type")
    ui_rows: int | None = Field(None, alias="ui:rows", description="Number of rows for textarea")
    ui_file_preview: bool | None = Field(None, alias="ui:filePreview", description="If true, show file preview")
    ui_submit_button_options: UISchemaSubmitButtonOptions | None = Field(None, alias="ui:submitButtonOptions")
    ui_enum_names: list[str | TranslatableText] | None = Field(
        None, alias="ui:enumNames", description="Custom labels for enum values"
    )

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        alias_generator = None
        extra = "allow"


class UIOptionsBaseType(GlobalUISchemaOptions):
    """Base type for UI options"""

    class_names: str | None = Field(None, alias="classNames")
    style: dict | None = Field(None, alias="style")
    title: str | TranslatableText | None = Field(None, alias="title")
    description: str | TranslatableText | None = Field(None, alias="description")
    placeholder: str | TranslatableText | None = Field(None, alias="placeholder")
    help: str | TranslatableText | None = Field(None, alias="help")
    autofocus: bool | None = Field(None, alias="autofocus")
    autocomplete: str | None = Field(None, alias="autocomplete")
    disabled: bool | None = Field(None, alias="disabled")
    empty_value: Any | None = Field(None, alias="emptyValue")
    enum_disabled: list[str | int | bool] | None = Field(None, alias="enumDisabled")
    hide_error: bool | None = Field(None, alias="hideError")
    readonly: bool | None = Field(None, alias="readonly")
    order: list[str] | None = Field(None, alias="order")
    file_preview: bool | None = Field(None, alias="filePreview")
    inline: bool | None = Field(None, alias="inline")
    input_type: str | None = Field(None, alias="inputType")
    rows: int | None = Field(None, alias="rows")
    submit_button_options: UISchemaSubmitButtonOptions | None = Field(None, alias="submitButtonOptions")
    widget: str | None = Field(None, alias="widget")
    enum_names: list[str | TranslatableText] | None = Field(None, alias="enumNames")

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        alias_generator = None
        extra = "allow"


class UiSchema(UIOptionsBaseTypeWithPrefix):
    """UI Schema for React JSON Schema Form"""

    ui_global_options: GlobalUISchemaOptions | None = Field(None, alias="ui:globalOptions")
    ui_root_field_id: str | None = Field(None, alias="ui:rootFieldId")
    ui_field: str | None = Field(None, alias="ui:field")
    ui_field_replaces_any_or_one_of: bool | None = Field(None, alias="ui:fieldReplacesAnyOrOneOf")
    ui_options: UIOptionsBaseType | dict | None = Field(None, alias="ui:options")

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        alias_generator = None
        extra = "allow"
