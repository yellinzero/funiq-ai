from loguru import logger

from providers.models.core.errors.validate import CredentialsValidateFailedError
from providers.models.core.model_provider import ModelProvider
from providers.models.core.models.model import ModelType


class AnthropicProvider(ModelProvider):
    provider_name = "anthropic"

    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials

        if validate failed, raise exception

        :param credentials: provider credentials, credentials form defined in `provider_credential_schema`.
        """
        try:
            model_instance = self.get_model_instance(ModelType.LLM)

            # Use `claude-3-opus-20240229` model for validate,
            model_instance.validate_credentials(model="claude-3-opus-20240229", credentials=credentials)
        except CredentialsValidateFailedError as ex:
            raise ex
        except Exception as ex:
            logger.exception(f"{self.get_provider_schema().provider} credentials validate failed")
            raise ex
