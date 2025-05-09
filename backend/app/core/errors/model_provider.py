from app.core.errors.base import BaseErrorCode


class ModelProviderErrorCode(BaseErrorCode):
    """
    Model provider related errors (Category C)
    """
    # Authentication & Authorization (01)
    CREDENTIALS_VALIDATE_FAILED = ("C0101", "Failed to validate provider credentials")

    # Resource related (03)
    PROVIDER_NOT_FOUND = ("C0301", "The provider is not found")
    MODEL_NOT_FOUND = ("C0302", "The model is not found")
    PROVIDER_ALREADY_EXISTS = ("C0303", "The provider already exists in this tenant")
    MODEL_ALREADY_EXISTS = ("C0304", "The model already exists in this tenant")
    FETCH_PROVIDERS_FAILED = ("C0305", "Failed to fetch providers")
    FETCH_MODELS_FAILED = ("C0306", "Failed to fetch models")
    
    # Operation related (04)
    SAVE_PROVIDER_FAILED = ("C0401", "Failed to save provider configuration")

    # Configuration related (08)
    INVALID_PROVIDER = ("C0801", "Invalid provider configuration")
    INVALID_MODEL = ("C0802", "Invalid model configuration")