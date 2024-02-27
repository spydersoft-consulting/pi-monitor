import logging
from pi_monitor import (
    MonitorSettings,
    NotificationSettings,
    StatusPageSettings,
    read_configuration,
)


def test_read_basic():
    settings: MonitorSettings = read_configuration("tests/testfiles/basic.config.json")
    assert settings.notification.smtp_sender_id == "smtp_sender_id"
    assert settings.notification.smtp_sender_apikey == "smtp_sender_apikey"
    assert settings.notification.sms_email == "sms_email"

    assert settings.status_page.api_key == "api_key"
    assert settings.status_page.page_id == "page_id"


def test_read_nofile(caplog):
    bad_file = "tests/testfiles/nothere.config.json"
    with caplog.at_level(logging.INFO):
        read_configuration(bad_file)
    assert (
        f"Configuration file not found: {bad_file}.  Using default"
        == caplog.records[0].message
    )


def test_return_defaults():
    bad_file = "tests/testfiles/nothere.config.json"
    default: MonitorSettings = MonitorSettings()
    default.notification = NotificationSettings()
    default.notification.smtp_sender_id = "hi"
    default.notification.smtp_sender_apikey = "key"
    default.notification.sms_email = "sms"
    default.status_page = StatusPageSettings()
    default.status_page.api_key = "api"
    default.status_page.page_id = "page"

    settings: MonitorSettings = read_configuration(bad_file, default)

    assert settings.notification.smtp_sender_id == "hi"
    assert settings.notification.smtp_sender_apikey == "key"
    assert settings.notification.sms_email == "sms"

    assert settings.status_page.api_key == "api"
    assert settings.status_page.page_id == "page"
