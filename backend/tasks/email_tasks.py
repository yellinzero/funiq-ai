import logging
import time

from celery import shared_task

from services.email_service import email_service
from utils.i18n import set_current_locale
from utils.template_renderer import template_renderer


@shared_task(queue="mail")
def send_signup_verification_email_task(language: str, to: str, code: str) -> str | None:
    """
    Asynchronously send a verification email with a code.

    :param language: Language for the email template (e.g., 'en', 'zh')
    :param to: Recipient email address
    :param code: Verification code
    :return: Message indicating success or failure
    """
    if not email_service.is_initialized:
        logging.error("Email service is not initialized. Cannot send verification email.")
        return None

    logging.info(f"Starting to send signup verification email to {to}.")
    start_at = time.perf_counter()

    try:
        set_current_locale(language)
        # Render the email content with the appropriate language template
        template_path = "signup_verification_email_template.html"
        html_content = template_renderer.render(template_path, to=to, code=code)

        # Send the email
        email_subject = "FuniqAi Signup Verification Code"
        email_service.send(to=to, subject=email_subject, html=html_content)

        # Calculate latency
        latency = time.perf_counter() - start_at
        logging.info(f"Successfully sent verification email to {to}. Latency: {latency:.2f}s")
        return "Success"
    except Exception as e:
        logging.exception(f"Failed to send verification email to {to}. Error: {e!s}")
        return None


@shared_task(queue="mail")
def send_reset_password_verification_email_task(language: str, to: str, code: str) -> str | None:
    """
    Asynchronously send a password reset verification email.

    :param language: Language for the email template (e.g., 'en', 'zh') 
    :param to: Recipient email address
    :param code: Verification code
    :return: Message indicating success or failure
    """
    if not email_service.is_initialized:
        logging.error("Email service is not initialized. Cannot send reset password email.")
        return None

    logging.info(f"Starting to send reset password verification email to {to}.")
    start_at = time.perf_counter()

    try:
        set_current_locale(language)
        # Render the email content with the appropriate language template
        template_path = "reset_password_verification_email_template.html"
        html_content = template_renderer.render(template_path, to=to, code=code)

        # Send the email
        email_subject = "Reset Your FuniqAi Password"
        email_service.send(to=to, subject=email_subject, html=html_content)

        # Calculate latency
        latency = time.perf_counter() - start_at
        logging.info(f"Successfully sent reset password email to {to}. Latency: {latency:.2f}s")
        return "Success"
    except Exception as e:
        logging.exception(f"Failed to send reset password email to {to}. Error: {e!s}")
        return None


@shared_task(queue="mail")
def send_activate_account_email_task(language: str, to: str, code: str) -> str | None:
    """
    Asynchronously send an account activation verification email.

    :param language: Language for the email template (e.g., 'en', 'zh')
    :param to: Recipient email address
    :param code: Verification code
    :return: Message indicating success or failure
    """
    if not email_service.is_initialized:
        logging.error("Email service is not initialized. Cannot send account activation email.")
        return None

    logging.info(f"Starting to send account activation email to {to}.")
    start_at = time.perf_counter()

    try:
        set_current_locale(language)
        # Render the email content with the appropriate language template
        template_path = "activation_verification_email_template.html"
        html_content = template_renderer.render(template_path, to=to, code=code)

        # Send the email
        email_subject = "Activate Your FuniqAi Account"
        email_service.send(to=to, subject=email_subject, html=html_content)

        # Calculate latency
        latency = time.perf_counter() - start_at
        logging.info(f"Successfully sent account activation email to {to}. Latency: {latency:.2f}s")
        return "Success"
    except Exception as e:
        logging.exception(f"Failed to send account activation email to {to}. Error: {e!s}")
        return None