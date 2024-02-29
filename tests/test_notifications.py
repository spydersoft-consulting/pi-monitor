import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from types import SimpleNamespace
from pi_monitor import Notifier, NotificationSettings
from unittest.mock import patch

TEST_SUCCESS_RESPONSE = SimpleNamespace(status_code=202)


def test_no_config(caplog):
    notifier: Notifier = Notifier(None)

    with caplog.at_level(logging.INFO):
        result = notifier.notify("Test", "Test")

    assert result
    assert caplog.records[0].message == "No configuration provided.  Skipping..."


def test_no_email(caplog):
    settings: NotificationSettings = NotificationSettings()
    settings.sms_email = ""
    notifier: Notifier = Notifier(settings)

    with caplog.at_level(logging.INFO):
        result = notifier.notify("Test", "Test")

    assert result
    assert (
        caplog.records[0].message
        == "No email address provided for notification.  Skipping..."
    )


@patch.object(SendGridAPIClient, "send", return_value=TEST_SUCCESS_RESPONSE)
def test_email(sendmail_send_mock, caplog):
    settings: NotificationSettings = NotificationSettings()
    settings.sms_email = "test@test.com"
    settings.smtp_sender_id = "sender@test.com"
    settings.smtp_sender_apikey = "apikey"
    settings.smtp_port = 587
    settings.smtp_url = "smtp.test.com"

    notifier: Notifier = Notifier(settings)

    with caplog.at_level(logging.INFO):
        result = notifier.notify("Test", "Test")

    assert sendmail_send_mock.called
    assert result
    assert caplog.records[0].message == f"Sending Notification to {settings.sms_email}"


@patch.object(SendGridAPIClient, "send", return_value=TEST_SUCCESS_RESPONSE)
def test_email_exception(sendmail_send_mock, caplog):
    sendmail_send_mock.side_effect = Exception("Test")
    settings: NotificationSettings = NotificationSettings()
    settings.sms_email = "test@test.com"
    settings.smtp_sender_id = "sender@test.com"
    settings.smtp_sender_apikey = "apikey"
    settings.smtp_port = 587
    settings.smtp_url = "smtp.test.com"

    notifier: Notifier = Notifier(settings)
    with caplog.at_level(logging.ERROR):
        result = notifier.notify("Test", "Test")
    
    assert sendmail_send_mock.called
    assert result is False
    assert caplog.records[0].message.startswith("Error sending mail:")