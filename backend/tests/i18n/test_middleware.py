from configs import funiq_ai_config
from utils.common.i18n import translation_registry


def test_middleware_set_locale_from_cookie(client):
    # Clear and load translations
    translation_registry._translations = {}
    translation_registry._supported_locales = set()
    translation_registry.load_translations("templates")
    
    client.cookies.set(funiq_ai_config.LANGUAGE_HEADER_NAME, "zh_CN")
    response = client.get("/locale/")
    assert response.status_code == 200
    assert response.text == "zh"


def test_middleware_set_default_locale(client):
    # Clear and load translations
    translation_registry._translations = {}
    translation_registry._supported_locales = set()
    translation_registry.load_translations("templates")
    
    response = client.get("/locale/")
    assert response.status_code == 200
    assert response.text == funiq_ai_config.DEFAULT_LOCALE


def test_middleware_with_cookie(client):
    client.cookies.set(funiq_ai_config.LANGUAGE_HEADER_NAME, "zh_CN")
    response = client.get("/locale/")
    assert response.status_code == 200
    assert response.text == "zh"


def test_middleware_with_unsupported_locale(client):
    client.cookies.set(funiq_ai_config.LANGUAGE_HEADER_NAME, "uk")
    response = client.get("/locale/")
    assert response.status_code == 200
    assert response.text == funiq_ai_config.DEFAULT_LOCALE


def test_middleware_translate_signup_title(client):
    # Test English (default)
    response = client.get("/signup-title/")
    assert response.status_code == 200
    assert response.text == "Signup Verification Code"

    # Test Chinese
    client.cookies.set(funiq_ai_config.LANGUAGE_HEADER_NAME, "zh_CN")
    response = client.get("/signup-title/")
    assert response.status_code == 200
    assert response.text == "注册验证码"


def test_middleware_translate_signup_content(client):
    # Test English (default)
    response = client.get("/signup-content/")
    assert response.status_code == 200
    assert response.text == "Please copy and paste this code into the verification form. This code is valid for the next 10 minutes only."

    # Test Chinese
    client.cookies.set(funiq_ai_config.LANGUAGE_HEADER_NAME, "zh_CN")
    response = client.get("/signup-content/")
    assert response.status_code == 200
    assert response.text == "请复制并粘贴此验证码到验证表单中。此验证码仅在接下来的10分钟内有效。"
