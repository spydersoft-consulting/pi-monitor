from pi_monitor import StatusPageClient
import logging
import requests
import pytest

TEST_PAGE_ID = "page-id"
TEST_API_KEY = "api-key"

TEST_INCIDENT_1 = {
    "id": "incident-id",
    "name": "test-incident",
    "components": [
        {
            "id": "component-id",
            "name": "test-component",
        },
        {
            "id": "component-id-2",
            "name": "test-component-2",
        },
    ],
}

TEST_INCIDENT_2 = {
    "id": "incident-id-2",
    "name": "test-incident-2",
    "components": [
        {
            "id": "component-id",
            "name": "test-component",
        }
    ],
}

TEST_MULTIPLE_INCIDENTS_RETURN = [TEST_INCIDENT_1, TEST_INCIDENT_2]


@pytest.fixture
def test_statuspage_client():
    return StatusPageClient(TEST_PAGE_ID, TEST_API_KEY)


def test_get_component(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    component_id: str = "component-id"
    expected_url: str = (
        f"{test_statuspage_client.STATUS_PAGE_BASE_URL}"
        f"/{page_id}/components/{component_id}"
    )
    requests_mock.get(expected_url, json={"status": "operational"})

    with caplog.at_level(logging.DEBUG):
        component: object = test_statuspage_client.get_component(component_id)

    assert requests_mock.called
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert component.status == "operational"
    assert (
        f"Retrieving component from StatusPage: {expected_url}"
        in caplog.records[0].message
    )


def test_get_component_not_found(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    component_id: str = "component-id"

    expected_url: str = (
        f"{test_statuspage_client.STATUS_PAGE_BASE_URL}"
        f"/{page_id}/components/{component_id}"
    )
    requests_mock.get(
        expected_url, json={"error": "Could not find component"}, status_code=404
    )

    with caplog.at_level(logging.DEBUG):
        component: object = test_statuspage_client.get_component(component_id)

    assert requests_mock.called
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert component.error == "Could not find component"
    assert (
        f"Retrieving component from StatusPage: {expected_url}"
        in caplog.records[0].message
    )


def test_get_component_exception(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    component_id: str = "component-id"

    expected_url: str = (
        f"{test_statuspage_client.STATUS_PAGE_BASE_URL}"
        f"/{page_id}/components/{component_id}"
    )
    requests_mock.get(
        expected_url,
        exc=requests.exceptions.ConnectTimeout,
    )

    with caplog.at_level(logging.DEBUG):
        component: object = test_statuspage_client.get_component(component_id)

    assert requests_mock.called
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert component is None
    assert (
        f"Retrieving component from StatusPage: {expected_url}"
        in caplog.records[0].message
    )
    assert caplog.records[1].message.startswith(
        test_statuspage_client.CLIENT_ERROR_MESSAGE
    )


def test_update_component(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    component_id: str = "component-id"

    expected_url: str = (
        f"{test_statuspage_client.STATUS_PAGE_BASE_URL}"
        f"/{page_id}/components/{component_id}"
    )
    requests_mock.put(expected_url, json={"name": "Test", "status": "operational"})
    payload = {"component": {"status": "operational"}}
    with caplog.at_level(logging.DEBUG):
        component: object = test_statuspage_client.update_component(
            component_id, payload
        )

    assert requests_mock.called
    assert requests_mock.last_request.json() == payload
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert component.name == "Test"
    assert component.status == "operational"
    assert f"Updating component {component_id}: {payload}" in caplog.records[0].message


def test_update_component_exception(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    component_id: str = "component-id"

    expected_url: str = (
        f"{test_statuspage_client.STATUS_PAGE_BASE_URL}"
        f"/{page_id}/components/{component_id}"
    )
    requests_mock.put(expected_url, exc=requests.exceptions.ConnectTimeout)
    payload = {"component": {"status": "operational"}}
    with caplog.at_level(logging.DEBUG):
        component: object = test_statuspage_client.update_component(
            component_id, payload
        )

    assert requests_mock.called
    assert requests_mock.last_request.json() == payload
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert component is None
    assert caplog.records[1].message.startswith(
        test_statuspage_client.CLIENT_ERROR_MESSAGE
    )


def test_get_unresolved_incidents(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    expected_url = (
        f"{test_statuspage_client.STATUS_PAGE_BASE_URL}/{page_id}/incidents/unresolved"
    )

    requests_mock.get(expected_url, json=TEST_MULTIPLE_INCIDENTS_RETURN)
    with caplog.at_level(logging.DEBUG):
        incidents: object = test_statuspage_client.get_unresolved_incidents()

    assert requests_mock.called
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert len(incidents) == 2
    assert incidents[0].name == "test-incident"
    assert incidents[0].components[0].name == "test-component"
    assert incidents[0].components[1].name == "test-component-2"


def test_get_unresolved_incidents_exception(
    caplog, requests_mock, test_statuspage_client
):
    page_id = test_statuspage_client.page_id

    expected_url = (
        f"{test_statuspage_client.STATUS_PAGE_BASE_URL}/{page_id}/incidents/unresolved"
    )
    requests_mock.get(expected_url, exc=requests.exceptions.ConnectTimeout)
    with caplog.at_level(logging.ERROR):
        incidents: object = test_statuspage_client.get_unresolved_incidents()

    assert requests_mock.called
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert incidents is None
    assert caplog.records[0].message.startswith(
        test_statuspage_client.CLIENT_ERROR_MESSAGE
    )


def test_create_incident(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    expected_url = f"{test_statuspage_client.STATUS_PAGE_BASE_URL}/{page_id}/incidents"

    payload = {
        "incident": {
            "name": "Test Incident",
            "status": "investigating",
            "body": "Incident Description",
            "component_ids": ["component-id"],
            "components": {"component-id": "major_outage"},
        }
    }

    requests_mock.post(expected_url, json=TEST_INCIDENT_1)
    with caplog.at_level(logging.DEBUG):
        incident: object = test_statuspage_client.create_incident(payload)

    assert requests_mock.called
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert incident.name == TEST_INCIDENT_1["name"]
    assert incident.components[0].name == TEST_INCIDENT_1["components"][0]["name"]
    assert incident.components[1].name == TEST_INCIDENT_1["components"][1]["name"]


def test_create_incident_exception(caplog, requests_mock, test_statuspage_client):
    page_id = test_statuspage_client.page_id
    expected_url = f"{test_statuspage_client.STATUS_PAGE_BASE_URL}/{page_id}/incidents"
    payload = {
        "incident": {
            "name": "Test Incident",
            "status": "investigating",
            "body": "Incident Description",
            "component_ids": ["component-id"],
            "components": {"component-id": "major_outage"},
        }
    }
    requests_mock.post(expected_url, exc=requests.exceptions.ConnectTimeout)
    with caplog.at_level(logging.ERROR):
        incidents: object = test_statuspage_client.create_incident(payload)

    assert requests_mock.called
    assert (
        requests_mock.last_request.headers[test_statuspage_client.AUTH_HEADER]
        == f"OAuth {test_statuspage_client.api_key}"
    )
    assert incidents is None
    assert caplog.records[0].message.startswith(
        test_statuspage_client.CLIENT_ERROR_MESSAGE
    )
