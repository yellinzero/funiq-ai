from collections.abc import Mapping

from loguru import logger

from providers.models.core.errors.validate import CredentialsValidateFailedError
from providers.models.core.model_provider import ModelProvider
from providers.models.core.models.model import ModelType


class OpenAIProvider(ModelProvider):
    provider_name = "openai"

    def validate_provider_credentials(self, credentials: Mapping) -> None:
        """
        Validate provider credentials
        if validate failed, raise exception

        :param credentials: provider credentials, credentials form defined in `provider_credential_schema`.
        """
        try:
            model_instance = self.get_model_instance(ModelType.LLM)

            # Use `gpt-4o-mini` model for validate,
            # no matter what model you pass in, text completion model or chat model
            model_instance.validate_credentials(model="gpt-4o-mini", credentials=credentials)
        except CredentialsValidateFailedError as ex:
            raise ex
        except Exception as ex:
            logger.exception(f"{self.get_provider_schema().provider} credentials validate failed")
            raise ex
