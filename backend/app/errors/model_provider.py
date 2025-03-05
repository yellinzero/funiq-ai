from app.errors.base import BaseErrorCode


class ModelProviderErrorCode(BaseErrorCode):
    """
    Model provider errors (Category M)
    """
    PROVIDER_NOT_FOUND = ("M0001", "The provider is not found")
    MODEL_NOT_FOUND = ("M0002", "The model is not found")
    PROVIDER_ALREADY_EXISTS = ("M0003", "The provider already exists in this tenant")
    MODEL_ALREADY_EXISTS = ("M0004", "The model already exists in this tenant")
    INVALID_PROVIDER = ("M0005", "Invalid provider configuration")
    INVALID_MODEL = ("M0006", "Invalid model configuration") 