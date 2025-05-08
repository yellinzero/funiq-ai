import time

from celery import shared_task
from loguru import logger

from infrastructure import email_service
from utils.common.i18n import gettext_lazy as _
from utils.common.i18n import set_current_locale
from utils.notification import email_template_renderer


def email_task(**kwargs):
    """
    Email task decorator with default retry settings
    """
    default_settings = {
        "queue": "mail",
        "autoretry_for": (Exception,),
        "retry_kwargs": {"max_retries": 3},
        "retry_backoff": True,
        "retry_backoff_max": 60,
        "retry_jitter": True,
    }
    settings = {**default_settings, **kwargs}
    return shared_task(**settings)


@email_task()
def send_signup_verification_email_task(language: str, to: str, code: str) -> str:
    """
    Asynchronously send a verification email with a code.

    :param language: Language for the email template (e.g., 'en', 'zh')
    :param to: Recipient email address
    :param code: Verification code
    :raises: Exception if email sending fails after all retries
    :return: "Success" if email is sent successfully
    """
    if not email_service.is_initialized:
        error_msg = "Email service is not initialized. Cannot send verification email."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info(f"Starting to send signup verification email to {to}.")
    start_at = time.perf_counter()

    try:
        set_current_locale(language)
        template_path = "signup_verification_email_template.html"
        html_content = email_template_renderer.render(template_path, to=to, code=code)

        email_subject = _("FuniqAi Signup Verification Code", domain="messages")
        email_service.send(to=to, subject=str(email_subject), html=html_content)

        latency = time.perf_counter() - start_at
        logger.info(f"Successfully sent verification email to {to}. Latency: {latency:.2f}s")
        return "Success"
    except Exception as e:
        logger.exception(f"Failed to send verification email to {to}. Error: {e!s}")
        raise


@email_task()
def send_reset_password_verification_email_task(language: str, to: str, code: str) -> str:
    """
    Asynchronously send a password reset verification email.

    :param language: Language for the email template (e.g., 'en', 'zh')
    :param to: Recipient email address
    :param code: Verification code
    :raises: Exception if email sending fails after all retries
    :return: "Success" if email is sent successfully
    """
    if not email_service.is_initialized:
        error_msg = "Email service is not initialized. Cannot send reset password email."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info(f"Starting to send reset password verification email to {to}.")
    start_at = time.perf_counter()

    try:
        set_current_locale(language)
        template_path = "reset_password_verification_email_template.html"
        html_content = email_template_renderer.render(template_path, to=to, code=code)

        email_subject = _("Reset Your FuniqAi Password", domain="messages")
        email_service.send(to=to, subject=str(email_subject), html=html_content)

        latency = time.perf_counter() - start_at
        logger.info(f"Successfully sent reset password email to {to}. Latency: {latency:.2f}s")
        return "Success"
    except Exception as e:
        logger.exception(f"Failed to send reset password email to {to}. Error: {e!s}")
        raise


@email_task()
def send_activate_account_email_task(language: str, to: str, code: str) -> str:
    """
    Asynchronously send an account activation verification email.

    :param language: Language for the email template (e.g., 'en', 'zh')
    :param to: Recipient email address
    :param code: Verification code
    :raises: Exception if email sending fails after all retries
    :return: "Success" if email is sent successfully
    """
    if not email_service.is_initialized:
        error_msg = "Email service is not initialized. Cannot send account activation email."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info(f"Starting to send account activation email to {to}.")
    start_at = time.perf_counter()

    try:
        set_current_locale(language)
        template_path = "activation_verification_email_template.html"
        html_content = email_template_renderer.render(template_path, to=to, code=code)

        email_subject = _("Activate Your FuniqAi Account", domain="messages")
        email_service.send(to=to, subject=str(email_subject), html=html_content)

        latency = time.perf_counter() - start_at
        logger.info(f"Successfully sent account activation email to {to}. Latency: {latency:.2f}s")
        return "Success"
    except Exception as e:
        logger.exception(f"Failed to send account activation email to {to}. Error: {e!s}")
        raise
