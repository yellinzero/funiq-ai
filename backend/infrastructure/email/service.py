from fastapi import FastAPI
from pydantic import EmailStr

from configs import funiq_ai_config
from utils.notification import SMTPClient


class EmailService:
    def __init__(self):
        self._client = None
        self._default_send_from = None

    @property
    def is_initialized(self) -> bool:
        """Check if the email client is initialized."""
        return self._client is not None

    def init(self):
        """Initialize the email client."""
        if funiq_ai_config.MAIL_DEFAULT_SEND_FROM:
            self._default_send_from = funiq_ai_config.MAIL_DEFAULT_SEND_FROM

        if not funiq_ai_config.SMTP_SERVER or not funiq_ai_config.SMTP_PORT:
            raise ValueError("SMTP_SERVER and SMTP_PORT are required for smtp mail type")
        if not funiq_ai_config.SMTP_USE_TLS and funiq_ai_config.SMTP_OPPORTUNISTIC_TLS:
            raise ValueError("SMTP_OPPORTUNISTIC_TLS is not supported without enabling SMTP_USE_TLS")
        self._client = SMTPClient(
            server=funiq_ai_config.SMTP_SERVER,
            port=funiq_ai_config.SMTP_PORT,
            username=funiq_ai_config.SMTP_USERNAME,
            password=funiq_ai_config.SMTP_PASSWORD,
            _from=funiq_ai_config.MAIL_DEFAULT_SEND_FROM,
            use_tls=funiq_ai_config.SMTP_USE_TLS,
            opportunistic_tls=funiq_ai_config.SMTP_OPPORTUNISTIC_TLS,
        )

    def send(self, to: EmailStr, subject: str, html: str, from_: str | None = None):
        """Send an email."""
        if not self._client:
            raise ValueError("Email client is not initialized")

        if not from_:
            from_ = self._default_send_from

        if not from_:
            raise ValueError("Email sender (from) is not set")

        if not to:
            raise ValueError("Email recipient (to) is not set")

        if not subject:
            raise ValueError("Email subject is not set")

        if not html:
            raise ValueError("Email content is not set")

        self._client.send(
            {
                "from": from_,
                "to": to,
                "subject": subject,
                "html": html,
            }
        )


# Initialize the email service in FastAPI
email_service = EmailService()


def init_email_service(app: FastAPI):
    """Initialize the email service with FastAPI."""
    email_service.init()
    app.state.email_service = email_service
