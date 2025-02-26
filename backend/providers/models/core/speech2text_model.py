import os
from abc import abstractmethod
from typing import IO

from pydantic import ConfigDict

from providers.models.core.base_model import AIModel
from providers.models.core.models.model import ModelType


class Speech2TextModel(AIModel):
    """
    Model class for speech2text model.
    """

    model_type: ModelType = ModelType.SPEECH2TEXT

    # pydantic configs
    model_config = ConfigDict(protected_namespaces=())

    def invoke(self, model: str, credentials: dict, file: IO[bytes], user: str | None = None) -> str:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param file: audio file
        :param user: unique user id
        :return: text for given audio file
        """
        try:
            return self._invoke(model, credentials, file, user)
        except Exception as e:
            raise self.transform_provider_error(e) from e

    @abstractmethod
    def _invoke(self, model: str, credentials: dict, file: IO[bytes], user: str | None = None) -> str:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param file: audio file
        :param user: unique user id
        :return: text for given audio file
        """
        raise NotImplementedError

    def _get_demo_file_path(self) -> str:
        """
        Get demo file for given model

        :return: demo file
        """
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the audio file
        return os.path.join(current_dir, "_assets/audio.mp3")
