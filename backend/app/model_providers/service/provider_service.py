from typing import List

from configs import funiq_ai_config
from providers.models.core.models.model import AIModelEntity
from providers.models.core.provider_factory import ProviderFactory

from ..schemas import ProviderInfo


class ProviderService:
    @staticmethod
    def get_all_providers() -> List[ProviderInfo]:
        providers = ProviderFactory.get_all_providers()
        provider_schemas = []
        
        for provider in providers:
            schema = provider.get_provider_schema()
            ui_schema = provider.get_provider_ui_schema()
            # Transform icon paths to full URLs with domain
            if schema.icon:
                base_url = funiq_ai_config.SERVER_URL.rstrip('/')  # get server url
                
                if schema.icon.get('small'):
                    schema.icon['small'] = f"{base_url}/static/providers/{schema.provider}/icon/small"
                if schema.icon.get('large'):
                    schema.icon['large'] = f"{base_url}/static/providers/{schema.provider}/icon/large"
            
            provider_schemas.append({
                **schema.model_dump(),
                "ui_schema": ui_schema
            })
            
        return provider_schemas
    
    @staticmethod
    def get_models(provider_name: str) -> List[AIModelEntity]:
        models = ProviderFactory.get_models(provider_name=provider_name)
        return models