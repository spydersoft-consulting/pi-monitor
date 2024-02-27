import json
from types import SimpleNamespace
from typing import Dict, List
import logging
import requests

logger = logging.getLogger(__name__)


class StatusPageClient:
    """StatusPageClient Class

    The StatusPageClient class provides methods for interacting with the
    [Statuspage.io's APIs](https://developer.statuspage.io/)

    Attributes:
        component_status_list: A list of valid component status codes for StatusPage.io
        incident_status_list: A list of valid incident status codes for live incidents
                                in StatusPage.io
        scheduled_incident_status_list: A list of valid incident status codes for
                                        scheduledStatusPage.io
    """

    component_status_list: List[str] = [
        "operational",
        "under_maintenance",
        "degraded_performance",
        "partial_outage",
        "major_outage",
    ]
    incident_status_list: List[str] = [
        "investigating",
        "identified",
        "monitoring",
        "resolved",
    ]
    scheduled_incident_status_list: List[str] = [
        "scheduled",
        "in_progress",
        "verifying",
        "complete",
    ]

    def __init__(self, api_key: str, page_id: str):
        self.api_key = api_key
        self.page_id = page_id

    def _get_headers(self) -> Dict[str, str]:
        """Retrieve headers for all requests

        This function adds the necessary `Authorization` and `Content-Type` headers
        for the API to operate using JSON.

        Returns:
            A Dictionary that represents the headers for request to Statuspage.io

        """
        return {
            "Authorization": str.format("OAuth {0}", self.api_key),
            "Content-Type": "application/json",
        }

    def get_component(self, component_id: str) -> object:
        """Retrieve Component Information

        Retrieve the current component information using the provided component_id.

        Args:
            component_id: The id of the component to retrieve.

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/getPagesPageIdComponentsComponentId).

        """
        component_url = str.format(
            "https://api.statuspage.io/v1/pages/{0}/components/{1}",
            self.page_id,
            component_id,
        )
        logger.info("Retrieving component from StatusPage: %s", component_url)
        try:
            component = requests.get(component_url, headers=self._get_headers())
            logger.info("Component Response: %s", component.text)
            return component.json(object_hook=lambda d: SimpleNamespace(**d))
        except Exception as e:
            logger.error("Request failed exception %s", e)

    def update_component(self, component_id: str, payload: object) -> object:
        """Update Component Information

        Update the given component using the provided payload as the object body.  The
        payload object will be processed using `json.dumps()`.

        Args:
            component_id: The id of the component to update.
            payload: An object representing the JSON payload.  Valid object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/putPagesPageIdComponentsComponentId).

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/putPagesPageIdComponentsComponentId).

        """
        component_url = str.format(
            "https://api.statuspage.io/v1/pages/{0}/components/{1}",
            self.page_id,
            component_id,
        )
        logger.debug("Updating component %s: %s", component_id, payload)
        r = requests.put(
            component_url, headers=self._get_headers(), data=json.dumps(payload)
        )
        return r.json(object_hook=lambda d: SimpleNamespace(**d))

    def get_unresolved_incidents(self) -> object:
        """Retrieve Unresolved Incidents

        Retrieve all the current unresolved incidents.

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/getPagesPageIdIncidentsUnresolved).

        """
        logger.info("Retrieving unresolved incidents")
        unresolved_incidents_url = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents/unresolved", self.page_id
        )
        unresolved_incidents_response = requests.get(
            unresolved_incidents_url, headers=self._get_headers()
        )
        result = unresolved_incidents_response.json(
            object_hook=lambda d: SimpleNamespace(**d)
        )
        return result

    def create_incident(self, payload: object) -> object:
        """Create Incident

        Create a new incident using the provided payload as the object body.  The
        payload object will be processed using `json.dumps()`.

        Args:
            payload: An object representing the JSON payload.  Valid object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/postPagesPageIdIncidents).

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/postPagesPageIdIncidents).

        """
        incident_url = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents", self.page_id
        )
        logger.info("Creating incident: %s", incident_url)
        r = requests.post(
            incident_url, headers=self._get_headers(), data=json.dumps(payload)
        )
        result_object = r.json(object_hook=lambda d: SimpleNamespace(**d))
        logger.debug("Create Incident Response: %s", result_object)
        return result_object

    def update_incident(self, incident_id: str, payload: object) -> object:
        """Update Incident Information

        Update the given incident using the provided payload as the object body.  The
        payload object will be processed using `json.dumps()`.

        Args:
            incident_id: The id of the incident to update.
            payload: An object representing the JSON payload.  Valid object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/patchPagesPageIdIncidentsIncidentId).

        Returns:
            A SimpleNamespace object created from the JSON return.  Object
                representation can be found in the
                [docs](https://developer.statuspage.io/#operation/patchPagesPageIdIncidentsIncidentId).

        """
        incident_url = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents/{1}",
            self.page_id,
            incident_id,
        )
        logger.info("Updating incident %s: %s", incident_url, incident_id)
        r = requests.patch(
            incident_url, headers=self._get_headers(), data=json.dumps(payload)
        )
        result_object = r.json(object_hook=lambda d: SimpleNamespace(**d))
        logger.debug("Update Incident Response: %s", result_object)
        return result_object
