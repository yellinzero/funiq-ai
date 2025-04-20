from app.core.errors.base import BaseErrorCode


class ModelProviderErrorCode(BaseErrorCode):
    """
    Model provider errors
    """
    PROVIDER_NOT_FOUND = ("C0001", "The provider is not found")
    MODEL_NOT_FOUND = ("C0002", "The model is not found")
    PROVIDER_ALREADY_EXISTS = ("C0003", "The provider already exists in this tenant")
    MODEL_ALREADY_EXISTS = ("C0004", "The model already exists in this tenant")
    INVALID_PROVIDER = ("C0005", "Invalid provider configuration")
    INVALID_MODEL = ("C0006", "Invalid model configuration") 