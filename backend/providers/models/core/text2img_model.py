from abc import abstractmethod
from typing import IO

from providers.models.core.base_model import AIModel
from providers.models.core.models.model import ModelType


class Text2ImageModel(AIModel):
    """
    Model class for text2img model.
    """

    model_type: ModelType = ModelType.TEXT2IMG

    def invoke(
        self, model: str, credentials: dict, prompt: str, model_parameters: dict, user: str | None = None
    ) -> list[IO[bytes]]:
        """
        Invoke Text2Image model

        :param model: model name
        :param credentials: model credentials
        :param prompt: prompt for image generation
        :param model_parameters: model parameters
        :param user: unique user id

        :return: image bytes
        """
        try:
            return self._invoke(model, credentials, prompt, model_parameters, user)
        except Exception as e:
            raise self.transform_provider_error(e) from e

    @abstractmethod
    def _invoke(
        self, model: str, credentials: dict, prompt: str, model_parameters: dict, user: str | None = None
    ) -> list[IO[bytes]]:
        """
        Invoke Text2Image model

        :param model: model name
        :param credentials: model credentials
        :param prompt: prompt for image generation
        :param model_parameters: model parameters
        :param user: unique user id

        :return: image bytes
        """
        raise NotImplementedError
