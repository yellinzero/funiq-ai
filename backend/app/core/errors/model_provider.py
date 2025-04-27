from app.core.errors.base import BaseErrorCode


class ModelProviderErrorCode(BaseErrorCode):
    """
    Model provider related errors (Category C)
    """
    # Resource related (03)
    PROVIDER_NOT_FOUND = ("C0301", "The provider is not found")
    MODEL_NOT_FOUND = ("C0302", "The model is not found")
    PROVIDER_ALREADY_EXISTS = ("C0303", "The provider already exists in this tenant")
    MODEL_ALREADY_EXISTS = ("C0304", "The model already exists in this tenant")
    
    # External service/integration (06)
    FETCH_PROVIDERS_FAILED = ("C0601", "Failed to fetch providers from external service")
    FETCH_MODELS_FAILED = ("C0602", "Failed to fetch models from external service")
    
    # Configuration related (08)
    INVALID_PROVIDER = ("C0801", "Invalid provider configuration")
    INVALID_MODEL = ("C0802", "Invalid model configuration")