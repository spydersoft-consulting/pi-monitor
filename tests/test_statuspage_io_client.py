from pi_monitor import StatusPageClient
import logging


def test_get_component(caplog, requests_mock):
    api_key: str = "api-key"
    page_id: str = "page-id"
    component_id: str = "component-id"

    client: StatusPageClient = StatusPageClient(api_key, page_id)
    expected_url: str = (
        f"https://api.statuspage.io/v1/pages/{page_id}/components/{component_id}"
    )
    requests_mock.get(expected_url, json={"status": "operational"})

    with caplog.at_level(logging.INFO):
        component: object = client.get_component(component_id)

    assert requests_mock.called
    assert component.status == "operational"
    assert (
        f"Retrieving component from StatusPage: {expected_url}"
        in caplog.records[0].message
    )


def test_get_component_not_found(caplog, requests_mock):
    api_key: str = "api-key"
    page_id: str = "page-id"
    component_id: str = "component-id"

    client: StatusPageClient = StatusPageClient(api_key, page_id)
    expected_url: str = (
        f"https://api.statuspage.io/v1/pages/{page_id}/components/{component_id}"
    )
    requests_mock.get(
        expected_url, json={"error": "Could not find component"}, status_code=404
    )

    with caplog.at_level(logging.INFO):
        component: object = client.get_component(component_id)

    assert requests_mock.called
    assert component.error == "Could not find component"
    assert (
        f"Retrieving component from StatusPage: {expected_url}"
        in caplog.records[0].message
    )
