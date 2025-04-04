from unittest.mock import MagicMock, patch

import pytest

from utils.notification import SMTPClient


@pytest.fixture
def smtp_client():
    return SMTPClient(
        server="smtp.example.com",
        port=587,
        username="test@example.com",
        password="password",  # noqa: S106
        _from="sender@example.com",
        use_tls=True,
    )


@patch("smtplib.SMTP_SSL")
def test_send_email_with_tls(mock_smtp, smtp_client):
    # Setup mock
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value = mock_smtp_instance

    # Test data
    mail = {"to": "recipient@example.com", "subject": "Test Subject", "html": "<p>Test content</p>"}

    # Send email
    smtp_client.send(mail)

    # Verify calls
    mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=10)
    mock_smtp_instance.login.assert_called_once_with("test@example.com", "password")
    assert mock_smtp_instance.sendmail.called
    mock_smtp_instance.quit.assert_called_once()
