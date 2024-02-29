import logging
import pytest
from pi_monitor import (
    StatusPageOperator,
    StatusPageSettings,
    OpLevel,
    StatusPageClient,
    Incident,
)
from types import SimpleNamespace
from unittest.mock import patch
from .statuspage_io_operator_objects import TestObjects

TEST_API_KEY = "apikey"
TEST_PAGE_ID = "pageid"


@pytest.fixture
def test_settings():
    settings: StatusPageSettings = StatusPageSettings()
    settings.api_key = TEST_API_KEY
    settings.page_id = TEST_PAGE_ID
    return settings


@pytest.fixture
def test_operator(test_settings):
    return StatusPageOperator(test_settings)


def test_no_config():
    operator: StatusPageOperator = None
    with pytest.raises(ValueError) as e:
        operator = StatusPageOperator(None)

    assert operator is None
    assert str(e.value) == "No configuration provided"


def test_config():
    settings: StatusPageSettings = StatusPageSettings()
    settings.api_key = TEST_API_KEY
    settings.page_id = TEST_PAGE_ID
    operator = StatusPageOperator(settings)

    assert operator.is_configured()
    assert operator.config == settings
    assert operator.client is not None


@patch.object(
    StatusPageClient, "get_component", return_value=TestObjects.GET_WORKING_COMPONENT
)
@patch.object(
    StatusPageClient, "update_component", return_value=TestObjects.UPDATE_RETURN
)
def test_update_component_status_nochange(update_mock, get_mock, test_operator):
    result = test_operator.update_component_status("component-id", OpLevel.Operational)

    assert get_mock.called
    assert update_mock.called is False
    assert result.status_changed is False


@patch.object(StatusPageClient, "get_component", return_value=None)
@patch.object(
    StatusPageClient, "update_component", return_value=TestObjects.UPDATE_RETURN
)
def test_update_component_status_get_error(
    update_mock, get_mock, test_operator, caplog
):
    component_id = "component-id"
    with caplog.at_level(logging.WARNING):
        result = test_operator.update_component_status(
            component_id, OpLevel.Operational
        )

    assert get_mock.called
    assert update_mock.called is False
    assert result.status_changed is False
    assert f"Failed to retrieve component {component_id}" == caplog.records[0].message


@patch.object(StatusPageClient, "update_incident", return_value=None)
@patch.object(StatusPageClient, "create_incident", return_value=[])
@patch.object(StatusPageClient, "get_unresolved_incidents", return_value=[])
@patch.object(
    StatusPageClient, "get_component", return_value=TestObjects.GET_WORKING_COMPONENT
)
@patch.object(
    StatusPageClient, "update_component", return_value=TestObjects.UPDATE_RETURN
)
def test_update_component_status_to_outage(
    update_mock,
    get_mock,
    unresolved_incident_mock,
    create_incident_mock,
    update_incident_mock,
    test_operator,
    caplog,
):
    component_id = "component-id"
    incident = Incident()
    incident.name = "Test Incident"

    description_dict = {
        OpLevel.Operational: "Operating Normally",
        OpLevel.Degraded: "Service Degraded",
        OpLevel.Partial_Outage: "Partial Service Outage",
        OpLevel.Full_Outage: "Major Service Outage",
    }
    incident.description = description_dict[OpLevel.Full_Outage]
    with caplog.at_level(logging.WARNING):
        result = test_operator.update_component_status(
            component_id, OpLevel.Full_Outage, incident
        )

    assert get_mock.called
    assert update_mock.called
    assert update_mock.call_args[0][0] == component_id

    assert unresolved_incident_mock.called

    assert create_incident_mock.called
    assert create_incident_mock.call_args[0][0]["incident"]["name"] == incident.name
    assert create_incident_mock.call_args[0][0]["incident"]["status"] == "investigating"

    assert update_incident_mock.called is False

    assert result.status_changed is True


@patch.object(StatusPageClient, "update_incident", return_value=None)
@patch.object(StatusPageClient, "create_incident", return_value=[])
@patch.object(StatusPageClient, "get_unresolved_incidents", return_value=None)
@patch.object(
    StatusPageClient, "get_component", return_value=TestObjects.GET_WORKING_COMPONENT
)
@patch.object(StatusPageClient, "update_component", return_value=None)
def test_update_component_status_to_outage_component_failed(
    update_mock,
    get_mock,
    unresolved_incident_mock,
    create_incident_mock,
    update_incident_mock,
    test_operator,
    caplog,
):
    component_id = "component-id"
    incident = Incident()
    incident.name = "Test Incident"

    description_dict = {
        OpLevel.Operational: "Operating Normally",
        OpLevel.Degraded: "Service Degraded",
        OpLevel.Partial_Outage: "Partial Service Outage",
        OpLevel.Full_Outage: "Major Service Outage",
    }
    incident.description = description_dict[OpLevel.Full_Outage]
    with caplog.at_level(logging.WARNING):
        result = test_operator.update_component_status(
            component_id, OpLevel.Full_Outage, incident
        )

    assert get_mock.called
    assert update_mock.called
    assert update_mock.call_args[0][0] == component_id

    assert unresolved_incident_mock.called

    assert create_incident_mock.called
    assert create_incident_mock.call_args[0][0]["incident"]["name"] == incident.name
    assert create_incident_mock.call_args[0][0]["incident"]["status"] == "investigating"

    assert update_incident_mock.called is False

    assert result.status_changed is True
    assert caplog.records[0].message == f"Failed to update component {component_id}"


@patch.object(StatusPageClient, "update_incident", return_value=None)
@patch.object(StatusPageClient, "create_incident", return_value=[])
@patch.object(
    StatusPageClient,
    "get_unresolved_incidents",
    return_value=TestObjects.UNRESOLVED_INCIDENTS,
)
@patch.object(
    StatusPageClient, "get_component", return_value=TestObjects.GET_DOWN_COMPONENT
)
@patch.object(
    StatusPageClient, "update_component", return_value=TestObjects.UPDATE_RETURN
)
def test_update_component_status_no_change_outage(
    update_mock,
    get_mock,
    unresolved_incident_mock,
    create_incident_mock,
    update_incident_mock,
    test_operator,
    caplog,
):
    component_id = "component-id"
    incident = Incident()
    incident.name = "Test Incident"

    description_dict = {
        OpLevel.Operational: "Operating Normally",
        OpLevel.Degraded: "Service Degraded",
        OpLevel.Partial_Outage: "Partial Service Outage",
        OpLevel.Full_Outage: "Major Service Outage",
    }
    incident.description = description_dict[OpLevel.Full_Outage]
    with caplog.at_level(logging.WARNING):
        result = test_operator.update_component_status(
            component_id, OpLevel.Full_Outage, incident
        )

    assert get_mock.called
    assert update_mock.called is False
    assert unresolved_incident_mock.called is False
    assert create_incident_mock.called is False
    assert update_incident_mock.called is False
    assert result.status_changed is False


@patch.object(StatusPageClient, "update_incident", return_value=None)
@patch.object(StatusPageClient, "create_incident", return_value=[])
@patch.object(
    StatusPageClient,
    "get_unresolved_incidents",
    return_value=TestObjects.UNRESOLVED_INCIDENTS,
)
@patch.object(
    StatusPageClient, "get_component", return_value=TestObjects.GET_DOWN_COMPONENT
)
@patch.object(
    StatusPageClient, "update_component", return_value=TestObjects.UPDATE_RETURN
)
def test_update_component_status_operational(
    update_mock,
    get_mock,
    unresolved_incident_mock,
    create_incident_mock,
    update_incident_mock,
    test_operator,
    caplog,
):
    component_id = "component-id"
    incident = Incident()
    incident.name = "Test Incident"

    description_dict = {
        OpLevel.Operational: "Operating Normally",
        OpLevel.Degraded: "Service Degraded",
        OpLevel.Partial_Outage: "Partial Service Outage",
        OpLevel.Full_Outage: "Major Service Outage",
    }
    incident.description = description_dict[OpLevel.Full_Outage]
    with caplog.at_level(logging.WARNING):
        result = test_operator.update_component_status(
            component_id, OpLevel.Operational, incident
        )

    assert get_mock.called
    assert update_mock.called
    assert update_mock.call_args[0][0] == component_id
    assert unresolved_incident_mock.called

    assert create_incident_mock.called is False

    assert update_incident_mock.called
    assert update_incident_mock.call_args[0][0] == TestObjects.EXISTING_INCIDENT.id

    assert result.status_changed
