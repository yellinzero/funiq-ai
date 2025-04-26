from typing import IO

from openai import OpenAI

from providers.models.core import Speech2TextModel
from providers.models.core.errors import CredentialsValidateFailedError
from providers.models.core.schemas import AIModelEntity, ModelType
from providers.models.openai.core import OpenAICore


class OpenAISpeech2TextModel(OpenAICore, Speech2TextModel):
    """
    Model class for OpenAI Speech to text model.
    """

    def _invoke(self, model: str, credentials: dict, file: IO[bytes], user: str | None = None) -> str:
        """
        Invoke speech2text model

        :param model: model name
        :param credentials: model credentials
        :param file: audio file
        :param user: unique user id
        :return: text for given audio file
        """
        return self._speech2text_invoke(model, credentials, file)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            audio_file_path = self._get_demo_file_path()

            with open(audio_file_path, "rb") as audio_file:
                self._speech2text_invoke(model, credentials, audio_file)
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex)) from ex

    def _speech2text_invoke(self, model: str, credentials: dict, file: IO[bytes]) -> str:
        """
        Invoke speech2text model

        :param model: model name
        :param credentials: model credentials
        :param file: audio file
        :return: text for given audio file
        """
        # transform credentials to kwargs for model instance
        credentials_kwargs = self._to_credential_kwargs(credentials)

        # init model client
        client = OpenAI(**credentials_kwargs)

        response = client.audio.transcriptions.create(model=model, file=file)

        return response.text

    def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity | None:
        """
        used to define customizable model schema
        """
        entity = AIModelEntity(
            model=model,
            label=model,
            model_type=ModelType.SPEECH2TEXT,
            model_properties={},
            parameter_rules_schema={},
        )

        return entity
