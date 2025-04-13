from abc import abstractmethod

from providers.models.core import AIModel
from providers.models.core.models import ModelType


class ModerationModel(AIModel):
    """
    Model class for moderation model.
    """

    model_type: ModelType = ModelType.MODERATION

    def invoke(self, model: str, credentials: dict, text: str, user: str | None = None) -> bool:
        """
        Invoke moderation model

        :param model: model name
        :param credentials: model credentials
        :param text: text to moderate
        :param user: unique user id
        :return: false if text is safe, true otherwise
        """
        self.start_invoke_timer()

        try:
            return self._invoke(model, credentials, text, user)
        except Exception as e:
            raise self.transform_provider_error(e) from e

    @abstractmethod
    def _invoke(self, model: str, credentials: dict, text: str, user: str | None = None) -> bool:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param text: text to moderate
        :param user: unique user id
        :return: false if text is safe, true otherwise
        """
        raise NotImplementedError
