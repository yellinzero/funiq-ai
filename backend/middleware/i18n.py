from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from configs import funiq_ai_config
from utils.common.i18n import set_current_locale

    
class I18nMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        locale_code = request.headers.get(
            funiq_ai_config.LANGUAGE_HEADER_NAME, funiq_ai_config.DEFAULT_LOCALE
        )
        if locale_code:
            logger.debug(f"I18nMiddleware: set locale to: {locale_code}")
            set_current_locale(locale_code)

        response = await call_next(request)
        return response