from loguru import logger

from providers.models.core import ModelProvider
from providers.models.core.errors import CredentialsValidateFailedError
from providers.models.core.schemas import ModelType


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

            # Use `claude_3_5_sonnet` model for validate,
            model_instance.validate_credentials(model="claude_3_5_sonnet", credentials=credentials)
        except CredentialsValidateFailedError as ex:
            raise ex
        except Exception as ex:
            logger.exception(f"{self.get_provider_schema().provider} credentials validate failed")
            raise ex
