import pytest
from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from middleware.i18n import I18nMiddleware
from utils.common.i18n import get_current_locale_code, translation_registry
from utils.common.i18n import gettext_lazy as _


@pytest.fixture
def load_translations():
    # Clear existing translations
    translation_registry._translations = {}
    translation_registry._supported_locales = set()

    # Load translations
    translation_registry.load_translations("templates")


async def signup_title(request: Request):
    return PlainTextResponse(_("Signup Verification Code", domain="templates"), status_code=200)


async def signup_content(request: Request):
    return PlainTextResponse(
        _(
            "Please copy and paste this code into the verification form. This code is valid for the next 10 minutes only.",
            domain="templates"
        ),
        status_code=200,
    )


async def locale_code(request: Request):
    return PlainTextResponse(get_current_locale_code(), status_code=200)


@pytest.fixture
def app(load_translations):
    app_ = FastAPI()
    
    app_.add_api_route("/signup-title/", signup_title)
    app_.add_api_route("/signup-content/", signup_content)
    app_.add_api_route("/locale/", locale_code)
    
    app_.add_middleware(I18nMiddleware)
    return app_


@pytest.fixture
def client(app):
    return TestClient(app)
