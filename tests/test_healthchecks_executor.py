from pi_monitor import (
    HealthCheckExecutor,
    StatusPageSettings,
    StatusPageOperator,
    Notifier,
    NotificationSettings,
    HealthCheckSettings,
    StatusPageComponentSettings,
)
import pytest
import logging
import requests
from unittest.mock import patch
from types import SimpleNamespace

TEST_API_KEY = "apikey"
TEST_PAGE_ID = "pageid"
TEST_URL = "http://test.com"
TEST_RESULT_DICT = {
    "status_changed": True,
    "incident_result": SimpleNamespace(
        **{
            "incident_created": True,
            "incident_resolved": False,
            "incident": SimpleNamespace(
                **{
                    "id": "incident-1",
                    "name": "Test Incident",
                    "description": "Incident Description",
                }
            ),
        }
    ),
}


@pytest.fixture
def test_settings():
    settings: StatusPageSettings = StatusPageSettings()
    settings.api_key = TEST_API_KEY
    settings.page_id = TEST_PAGE_ID
    return settings


@pytest.fixture
def test_operator(test_settings):
    return StatusPageOperator(test_settings)


@pytest.fixture
def test_notifier():
    settings: NotificationSettings = NotificationSettings()
    settings.sms_email = ""
    return Notifier(settings)


@pytest.fixture
def test_executor(test_operator, test_notifier):
    return HealthCheckExecutor(test_operator, test_notifier)


def test_construct_result(test_operator, test_notifier):
    executor = HealthCheckExecutor(test_operator, test_notifier)

    assert executor.statuspage_operator == test_operator
    assert executor.notifier == test_notifier


def test_execute_health_check_pass(caplog, requests_mock, test_executor):
    settings: HealthCheckSettings = HealthCheckSettings()
    settings.name = "Test"
    settings.url = TEST_URL
    settings.status_page = None
    requests_mock.get(settings.url, text="OK", status_code=200)

    with caplog.at_level(logging.INFO):
        test_executor.execute_health_check(settings)

    assert f"Checking {settings.name}..." == caplog.records[0].message
    assert "Status OK" == caplog.records[1].message


def test_execute_health_check_nourl(caplog, requests_mock, test_executor):
    settings: HealthCheckSettings = HealthCheckSettings()
    settings.name = "Test"
    settings.url = ""
    settings.status_page = None
    requests_mock.get(settings.url, text="OK", status_code=200)

    with caplog.at_level(logging.INFO):
        test_executor.execute_health_check(settings)

    assert f"Checking {settings.name}..." == caplog.records[0].message
    assert "no url defined" == caplog.records[1].message


@patch.object(Notifier, "notify", return_value=None)
def test_execute_health_check_fail(notify_mock, caplog, requests_mock, test_executor):
    settings: HealthCheckSettings = HealthCheckSettings()
    settings.name = "Test"
    settings.url = TEST_URL
    settings.status_page = None
    requests_mock.get(settings.url, text="Page Not Found", status_code=404)

    with caplog.at_level(logging.INFO):
        test_executor.execute_health_check(settings)

    assert caplog.records[0].levelno == logging.INFO
    assert f"Checking {settings.name}..." == caplog.records[0].message

    assert (
        "Request failed with Response Code 404: Page Not Found"
        == caplog.records[1].message
    )
    assert "404 Page Not Found" == caplog.records[2].message

    assert notify_mock.called
    assert notify_mock.call_args[0][0] == settings.name
    assert notify_mock.call_args[0][1] == "404 Page Not Found"


@patch.object(Notifier, "notify", return_value=None)
def test_execute_health_check_exception(
    notify_mock, caplog, requests_mock, test_executor
):
    settings: HealthCheckSettings = HealthCheckSettings()
    settings.name = "Test"
    settings.url = TEST_URL
    settings.status_page = None
    requests_mock.get(settings.url, exc=requests.exceptions.ConnectTimeout)

    with caplog.at_level(logging.INFO):
        test_executor.execute_health_check(settings)

    assert caplog.records[0].levelno == logging.INFO
    assert f"Checking {settings.name}..." == caplog.records[0].message

    assert caplog.records[1].message.startswith("Request failed exception")
    assert "Unknown status failure" == caplog.records[2].message

    assert notify_mock.called
    assert notify_mock.call_args[0][0] == settings.name
    assert notify_mock.call_args[0][1] == "Unknown status failure"


@patch.object(
    StatusPageOperator,
    "update_component_status",
    return_value=SimpleNamespace(**TEST_RESULT_DICT),
)
@patch.object(Notifier, "notify", return_value=None)
def test_execute_health_check_status_page_notify(
    notify_mock, update_component_status, caplog, requests_mock, test_executor
):
    status_page_setting = StatusPageComponentSettings()
    status_page_setting.component_id = "component-id"

    settings: HealthCheckSettings = HealthCheckSettings()
    settings.name = "Test"
    settings.url = TEST_URL
    settings.status_page = status_page_setting
    requests_mock.get(settings.url, text="Page Not Found", status_code=404)

    with caplog.at_level(logging.INFO):
        test_executor.execute_health_check(settings)

    assert caplog.records[0].levelno == logging.INFO
    assert f"Checking {settings.name}..." == caplog.records[0].message

    assert update_component_status.called
    assert update_component_status.call_args[0][0] == settings.status_page.component_id

    assert notify_mock.called
    assert notify_mock.call_args[0][0] == settings.name
    assert notify_mock.call_args[0][1] == "Incident Description"
