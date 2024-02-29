from types import SimpleNamespace


class TestObjects:
    UPDATE_RETURN = SimpleNamespace(id="component-id")
    GET_WORKING_COMPONENT = SimpleNamespace(id="component-id", status="operational")
    GET_DOWN_COMPONENT = SimpleNamespace(id="component-id", status="major_outage")
    EXISTING_INCIDENT = SimpleNamespace(
        id="incident-id",
        components=[
            SimpleNamespace(id="component-id"),
            SimpleNamespace(id="component-id-2"),
        ],
    )
    EXISTING_INCIDENT_2 = SimpleNamespace(
        id="incident-id-2",
        components=[
            SimpleNamespace(id="component-id-2"),
        ],
    )
    UNRESOLVED_INCIDENTS = [EXISTING_INCIDENT, EXISTING_INCIDENT_2]
