import json
from types import SimpleNamespace
import logging
import requests

logger = logging.getLogger(__name__)


class StatusPageClient:

    component_status_list = ['operational', 'under_maintenance',
                             'degraded_performance', 'partial_outage', 'major_outage']
    incident_status_list = ['investigating',
                            'identified', 'monitoring', 'resolved']
    scheduled_incident_status_list = [
        'scheduled', 'in_progress', 'verifying', 'complete']

    def __init__(self, apiKey: str, pageId: str):
        self.apiKey = apiKey
        self.pageId = pageId

    def getHeaders(self):
        return {'Authorization': str.format('OAuth {0}', self.apiKey), 'Content-Type': 'application/json'}

    def getComponent(self, componentId: str):
        componentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/components/{1}", self.pageId, componentId)
        logger.info("Retrieving component from StatusPage: %s", componentUrl)
        component = requests.get(componentUrl, headers=self.getHeaders())
        return component.json(object_hook=lambda d: SimpleNamespace(**d))

    def updateComponent(self, componentId: str, payload: any):
        componentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/components/{1}", self.pageId, componentId)
        logger.debug("Updating component %s: %s", componentId, payload)
        r = requests.put(componentUrl, headers=self.getHeaders(),
                         data=json.dumps(payload))
        return r.json()

    def getUnresolvedIncidents(self):
        logger.info("Retrieving unresolved incidents")
        unresolvedIncidentsUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents/unresolved", self.pageId)
        unresolvedIncidentsResponse = requests.get(
            unresolvedIncidentsUrl, headers=self.getHeaders())
        result = unresolvedIncidentsResponse.json(
            object_hook=lambda d: SimpleNamespace(**d))
        return result

    def createIncident(self, payload: any):
        incidentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents", self.pageId)
        logger.info("Creating incident: %s", incidentUrl)
        r = requests.post(incidentUrl, headers=self.getHeaders(),
                          data=json.dumps(payload))
        logger.debug("Response: %s", r.json())

    def updateIncident(self, incidentId: str, payload: any):
        incidentUrl = str.format(
            "https://api.statuspage.io/v1/pages/{0}/incidents/{1}", self.pageId, incidentId)
        logger.info("Closing incident %s: %s", incidentUrl, incidentId)
        r = requests.patch(
            incidentUrl, headers=self.getHeaders(), data=json.dumps(payload))
        logger.debug("Response: %s", r.json())
