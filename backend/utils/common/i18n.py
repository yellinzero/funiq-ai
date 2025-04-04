from __future__ import annotations

import os
from collections import deque
from dataclasses import dataclass
from typing import Annotated, Any, Callable, ClassVar

from babel.core import Locale as BabelLocale
from babel.support import LazyProxy, NullTranslations, Translations
from loguru import logger
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core.core_schema import with_info_plain_validator_function

from configs import funiq_ai_config
from utils.common.context import ContextStorage

all_domains = ["templates", "providers"]


class TranslationRegistry:
    """
    A registry that manages translations for multiple domains (e.g., messages, email, providers).
    Handles loading and storing translations for different languages and domains.
    """

    _translations: ClassVar[dict[str, dict[str, NullTranslations]]] = {}  # domain -> language -> translations
    _default_locale: ClassVar[str] = funiq_ai_config.DEFAULT_LOCALE
    _supported_locales: ClassVar[set[str]] = set()
    _locales_path: ClassVar[str] = funiq_ai_config.LOCALES_PATH

    @property
    def translations(self) -> dict[str, dict[str, NullTranslations]]:
        """Returns all loaded translations across all domains and languages."""
        return self._translations

    @property
    def supported_locales(self) -> set[str]:
        """Returns set of all supported locale codes."""
        return self._supported_locales

    @property
    def default_locale(self) -> str:
        """Returns the default locale code."""
        return self._default_locale

    def load_translations(self, domain: str = "messages") -> None:
        """
        Load translations for a specific domain from the locales directory.
        Updates the supported locales set based on available translations.

        Args:
            domain: The translation domain to load (e.g., 'messages', 'email')
        """
        if domain not in self._translations:
            self._translations[domain] = {}

        for lang in os.listdir(self._locales_path):
            if os.path.isfile(os.path.join(self._locales_path, lang)):
                continue
            try:
                translation = Translations.load(self._locales_path, [lang], domain)
                if lang in self._translations[domain]:
                    self._translations[domain][lang].merge(translation)
                else:
                    self._translations[domain][lang] = translation
            except Exception as e:
                logger.error(f"Cannot load translation for '{lang}' in domain '{domain}': {e!s}")
                continue

        # Update supported locales based on all domains
        all_locales = set()
        for domain_translations in self._translations.values():
            all_locales.update(domain_translations.keys())
        self._supported_locales = all_locales
        self._supported_locales.add(self.default_locale)
        logger.info(f"Supported locales for domain '{domain}': {sorted(self._supported_locales)}")

    def register_domains(self, domains: list[str]) -> None:
        """
        Register and load translations for multiple domains at once.

        Args:
            domains: List of domain names to register (e.g., ['messages', 'email', 'providers'])
        """
        for domain in domains:
            self.load_translations(domain)
            logger.info(f"Registered translations for domain: {domain}")


# Global translation registry instance
translation_registry = TranslationRegistry()


@dataclass
class LocaleTranslator:
    """
    Handles locale-specific translations and stores locale information.
    Wraps Babel's Locale functionality with translation capabilities.
    """

    language: str
    translations: NullTranslations
    territory: str | None = None
    script: str | None = None
    variant: str | None = None
    modifier: str | None = None

    @classmethod
    def get(cls, locale_code: str) -> LocaleTranslator:
        """
        Create a LocaleTranslator instance for the given locale code.
        Falls back to default locale if the requested locale is not supported.

        Args:
            locale_code: The locale code (e.g., 'en', 'zh-CN')

        Returns:
            LocaleTranslator instance for the requested or default locale
        """
        if locale_code not in translation_registry.supported_locales:
            locale_code = translation_registry.default_locale

        babel_locale = BabelLocale.parse(locale_code)
        default_translations = translation_registry.translations.get("messages", {}).get(
            locale_code, NullTranslations()
        )

        return cls(
            language=babel_locale.language,
            translations=default_translations,
            territory=babel_locale.territory,
            script=babel_locale.script,
            variant=babel_locale.variant,
            modifier=babel_locale.modifier,
        )

    def translate(
        self,
        message: str,
        plural_message: str | None = None,
        count: int | None = None,
        domain: str = "messages",
        **kwargs: str,
    ) -> str:
        """
        Translate a message using the loaded translations for the specified domain.
        """
        locale_code = self.language
        if self.territory:
            locale_code = f"{self.language}_{self.territory}"

        translations = translation_registry.translations.get(domain, {}).get(locale_code, NullTranslations())

        if plural_message is not None and count is not None:
            message = translations.ungettext(message, plural_message, count)
            format_kwargs = {"count": str(count), **kwargs}  # Create new dict with count, preserving user's kwargs
        else:
            message = translations.ugettext(message)
            format_kwargs = kwargs

        return message.format(**format_kwargs) if format_kwargs else message


class LocaleContext(ContextStorage):
    """
    Context manager for handling locale information in the current context.
    Provides thread-local storage for the current locale.
    """

    DEFAULT_VALUE = LocaleTranslator.get(funiq_ai_config.DEFAULT_LOCALE)
    CONTEXT_KEY_NAME = "locale"


# Global locale context instance
_locale_ctx = LocaleContext()


def create_lazy_translator(translation_func: Callable) -> Callable:
    """
    Create a lazy translation function that defers actual translation until the string is used.

    Args:
        translation_func: The function to use for actual translation

    Returns:
        A function that creates LazyProxy objects for delayed translation
    """

    def lazy_translator(
        string: LazyProxy | str,
        *args: Any,
        locale: str | None = None,
        **kwargs: Any,
    ) -> LazyProxy | str:
        if isinstance(string, LazyProxy):
            return string

        if "enable_cache" not in kwargs:
            kwargs["enable_cache"] = False

        return LazyProxy(translation_func, string, *args, locale=locale, **kwargs)

    return lazy_translator


def _translate(
    message: str,
    plural_message: str | None = None,
    count: int | None = None,
    **kwargs: Any,
):
    """
    Internal translation function that handles the actual translation process.

    Args:
        message: The message to translate
        plural_message: Optional plural form of the message
        count: Optional count for plural forms
        **kwargs: Additional translation parameters
    """
    locale_code = kwargs.pop("locale", None)
    domain = kwargs.pop("domain", "messages")
    locale = LocaleTranslator.get(locale_code) if locale_code else _locale_ctx.get()
    return locale.translate(message, plural_message, count, domain=domain, **kwargs)


# Create global lazy translation function
gettext_lazy = create_lazy_translator(_translate)


# Utility functions for managing translations and locales
def load_domain_translations(domain: str) -> None:
    """Load translations for a specific domain."""
    translation_registry.load_translations(domain)


def register_translation_domains(domains: list[str]) -> None:
    """Register and load translations for multiple domains at once."""
    translation_registry.register_domains(domains)


def set_current_locale(locale_code: str) -> None:
    """Set the current locale in the context."""
    locale = LocaleTranslator.get(locale_code)
    _locale_ctx.set(locale)


def get_current_locale_translator() -> LocaleTranslator:
    """Get the current locale from the context."""
    locale: LocaleTranslator = _locale_ctx.get()
    return locale


def get_current_locale_code() -> str:
    """Get the language code of the current locale."""
    return str(get_current_locale_translator().language)


def get_current_locale_code_with_territory() -> str:
    """Get the language code of the current locale."""
    locale = get_current_locale_translator()
    return locale.language if locale.territory is None else f"{locale.language}_{locale.territory}"


def get_current_territory() -> str:
    """Get the territory code of the current locale."""
    return str(get_current_locale_translator().territory)


def get_current_variant() -> str:
    """Get the variant code of the current locale."""
    return str(get_current_locale_translator().variant)


def register_all_translation_domains() -> None:
    """Register and load translations for multiple domains at once."""
    translation_registry.register_domains(all_domains)


def translate_text(text: LazyProxy | str | None) -> str | None:
    """
    Translate a single text that might be a LazyProxy or regular string.

    Args:
        text: Text to translate, can be LazyProxy, str, or None

    Returns:
        Translated string or None if input is None
    """
    if text is None:
        return None
    return str(text) if isinstance(text, (LazyProxy, str)) else text


def translate_data(data: Any) -> Any:
    """
    Iteratively translate all LazyProxy objects within a Python data structure.
    Handles dictionaries, lists, tuples and basic data types.
    Prevents infinite loops from circular references.

    Args:
        data: Any Python data structure that might contain LazyProxy objects

    Returns:
        Data structure with all LazyProxy objects translated to strings
    """
    # Fast path for simple types
    if isinstance(data, (str, int, float, bool, LazyProxy)) or data is None:
        return str(data) if isinstance(data, LazyProxy) else data

    # Track processed objects to prevent infinite loops
    processed_objects = set()

    # Stack for iterative processing
    stack = deque([(data, None, None)])  # (value, parent, key/index)
    root = None

    while stack:
        value, parent, key = stack.popleft()

        # Skip already processed objects
        value_id = id(value)
        if value_id in processed_objects:
            continue

        # Only track container types
        if isinstance(value, (dict, list, tuple, set)):
            processed_objects.add(value_id)

        # Create new container if needed
        if isinstance(value, dict):
            new_value = {}
            if root is None:
                root = new_value
            if parent is not None:
                if isinstance(parent, (list, tuple)):
                    parent[key] = new_value
                elif isinstance(parent, set):
                    parent.remove(value)
                    parent.add(new_value)
                else:
                    parent[key] = new_value
            # Add all items to stack
            stack.extend((v, new_value, k) for k, v in value.items())

        elif isinstance(value, (list, tuple)):
            is_list = isinstance(value, list)
            new_value = []  # use list instead of tuple to avoid type error first
            if root is None:
                root = new_value
            if parent is not None:
                if isinstance(parent, (list, tuple)):
                    parent[key] = new_value
                elif isinstance(parent, set):
                    parent.remove(value)
                    parent.add(new_value)
                else:
                    parent[key] = new_value

            # pre-allocate list size
            if is_list:
                new_value.extend([None] * len(value))

            # Add all items to stack
            stack.extend((v, new_value, i) for i, v in enumerate(value))

            # if it's a tuple, convert it last
            if not is_list and parent is not None:
                if isinstance(parent, (list, tuple)):
                    parent[key] = tuple(new_value)
                elif isinstance(parent, set):
                    parent.remove(new_value)
                    parent.add(tuple(new_value))
                else:
                    parent[key] = tuple(new_value)

        elif isinstance(value, set):
            new_value = set()
            if root is None:
                root = new_value
            if parent is not None:
                if isinstance(parent, (list, tuple)):
                    parent[key] = new_value
                elif isinstance(parent, set):
                    parent.remove(value)
                    parent.add(new_value)
                else:
                    parent[key] = new_value
            # Add all items to stack
            stack.extend((v, new_value, None) for v in value)

        else:
            # Handle leaf nodes (including LazyProxy)
            translated = str(value) if isinstance(value, LazyProxy) else value
            if parent is not None:
                if isinstance(parent, (list, tuple)):
                    parent[key] = translated
                elif isinstance(parent, set):
                    parent.add(translated)
                else:
                    parent[key] = translated
            else:
                root = translated

    return root if root is not None else data


class LazyProxyAnnotation:
    """Annotation for LazyProxy type validation and translation"""

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string"}

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> Any:
        def validate_and_translate(value: str | LazyProxy, _: Any) -> str:
            return translate_text(value)

        return with_info_plain_validator_function(validate_and_translate)


TranslatableText = Annotated[str | LazyProxy, LazyProxyAnnotation]
