import json
from types import SimpleNamespace
from typing import Dict, List
import logging
import requests

logger = logging.getLogger(__name__)


class StatusPageClient:
    """StatusPageClient Class

    The StatusPageClient class provides methods for interacting with the [Statuspage.io's APIs](https://developer.statuspage.io/)

    Attributes:
        component_status_list: A list of valid component status codes for StatusPage.io
        incident_status_list: A list of valid incident status codes for live incidents in StatusPage.io
        scheduled_incident_status_list: A list of valid incident status codes for scheduledStatusPage.io
    """

    component_status_list: List[str] = ['operational', 'under_maintenance',
                             'degraded_performance', 'partial_outage', 'major_outage']
    incident_status_list: List[str] = ['investigating',
                            'identified', 'monitoring', 'resolved']
    scheduled_incident_status_list: List[str] = [
        'scheduled', 'in_progress', 'verifying', 'complete']

    def __init__(self, apiKey: str, pageId: str):
        self.apiKey = apiKey
        self.pageId = pageId

    def _getHeaders(self) -> Dict[str, str]:
        """  Retrieve headers for all requests

        This function adds the necessary `Authorization` and `Content-Type` headers for the API to operate using JSON.

        Returns:
            A Dictionary that represents the headers for request to Statuspage.io

        """
        return {'Authorization': str.format('OAuth {0}', self.apiKey), 'Content-Type': 'application/json'}

    def getComponent(self, componentId: str) -> object:
        """  Retrieve Component Information

        Retrieve the current component information using the provided componentId.  

        Args:
            componentId: The id of the component to retrieve.

        Returns:
            A SimpleNamespace object created from the JSON return.  Object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/getPagesPageIdComponentsComponentId).

        """
        componentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/components/{1}", self.pageId, componentId)
        logger.info("Retrieving component from StatusPage: %s", componentUrl)
        component = requests.get(componentUrl, headers=self.getHeaders())
        return component.json(object_hook=lambda d: SimpleNamespace(**d))

    def updateComponent(self, componentId: str, payload: object) -> object:
        """  Update Component Information

        Update the given component using the provided payload as the object body.  The payload object will be processed using `json.dumps()`.

        Args:
            componentId: The id of the component to update.
            payload: An object representing the JSON payload.  Valid object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/putPagesPageIdComponentsComponentId). 

        Returns:
            A SimpleNamespace object created from the JSON return.  Object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/putPagesPageIdComponentsComponentId).

        """
        componentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/components/{1}", self.pageId, componentId)
        logger.debug("Updating component %s: %s", componentId, payload)
        r = requests.put(componentUrl, headers=self.getHeaders(),
                         data=json.dumps(payload))
        return r.json(object_hook=lambda d: SimpleNamespace(**d))

    def getUnresolvedIncidents(self) -> object:
        """  Retrieve Unresolved Incidents

        Retrieve all the current unresolved incidents.

        Returns:
            A SimpleNamespace object created from the JSON return.  Object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/getPagesPageIdIncidentsUnresolved).

        """
        logger.info("Retrieving unresolved incidents")
        unresolvedIncidentsUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents/unresolved", self.pageId)
        unresolvedIncidentsResponse = requests.get(
            unresolvedIncidentsUrl, headers=self.getHeaders())
        result = unresolvedIncidentsResponse.json(
            object_hook=lambda d: SimpleNamespace(**d))
        return result

    def createIncident(self, payload: object) -> object:
        """  Create Incident

        Create a new incident using the provided payload as the object body.  The payload object will be processed using `json.dumps()`.

        Args:
            payload: An object representing the JSON payload.  Valid object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/postPagesPageIdIncidents). 

        Returns:
            A SimpleNamespace object created from the JSON return.  Object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/postPagesPageIdIncidents).

        """
        incidentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents", self.pageId)
        logger.info("Creating incident: %s", incidentUrl)
        r = requests.post(incidentUrl, headers=self.getHeaders(),
                          data=json.dumps(payload))
        resultObject = r.json(object_hook=lambda d: SimpleNamespace(**d))
        logger.debug("Create Incident Response: %s", resultObject)
        return resultObject

    def updateIncident(self, incidentId: str, payload: object) -> object:
        """  Update Incident Information

        Update the given incident using the provided payload as the object body.  The payload object will be processed using `json.dumps()`.

        Args:
            incidentId: The id of the incident to update.
            payload: An object representing the JSON payload.  Valid object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/patchPagesPageIdIncidentsIncidentId). 

        Returns:
            A SimpleNamespace object created from the JSON return.  Object representation can be found in the [Statuspage.io docs](https://developer.statuspage.io/#operation/patchPagesPageIdIncidentsIncidentId).

        """
        incidentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents/{1}", self.pageId, incidentId)
        logger.info("Updating incident %s: %s", incidentUrl, incidentId)
        r = requests.patch(
            incidentUrl, headers=self.getHeaders(), data=json.dumps(payload))
        resultObject = r.json(object_hook=lambda d: SimpleNamespace(**d))
        logger.debug("Update Incident Response: %s", resultObject)
        return resultObject
