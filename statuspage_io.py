import json
from types import SimpleNamespace
import logging
import statuspage_io_client

logger = logging.getLogger(__name__)

class Incident:
    name = "Incident Name"
    description = "Incident Description"

class IncidentResult:
    incidentCreated = False
    incidentResolved = False

    def __init__(self):
        self.incidentCreated = False
        self.incidentResolved = False

class StatusResult:
    statusChanged = False
    incidentResult = IncidentResult()
    
    def __init__(self):
        self.incidentResult = IncidentResult()

class StatusPageOperator:

    def __init__(self):
        self.config = self.getConfig()
        self.client = statuspage_io_client.StatusPageClient(self.config.apiKey, self.config.pageId)

    def getConfig(self):
        with open('statuspage_io.config.json') as f:
            configData = json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d))
        return configData

    def checkAndUpdateComponentStatus(self, componentId, componentStatus, incidentDetails: Incident=Incident()):
        if (componentStatus not in self.client.component_status_list):
            raise ValueError(str.format("Invalid status '{0}'.  Valid values are {1}", componentStatus, self.client.component_status_list))

        result = StatusResult()
        component = self.client.getComponent(componentId)

        if (component.status != componentStatus):
            result.statusChanged = True
            logger.info("Changing status from %s to %s", component.status, componentStatus)
            self.updateComponentStatus(componentId, componentStatus)
            result.incidentResult = self.checkAndLogIncident(componentId, component.status, componentStatus, incidentDetails)

        return result

    def updateComponentStatus(self, componentId, newComponentStatus):
        if (newComponentStatus not in self.client.component_status_list):
            raise ValueError(str.format("Invalid status '{0}'.  Valid values are {1}", newComponentStatus, self.client.component_status_list))

        logger.debug("Setting component status to %s: %s", newComponentStatus, componentId)
        payload = { "component": { "status": newComponentStatus } }
        self.client.updateComponent(componentId, payload)

    def filter_set(self, incidents, componentId):
        def iterator_func(incident):
            for comp in incident.components:
                if comp.id == componentId:
                    return True
            return False
        
        return filter(iterator_func, incidents)


    def checkAndLogIncident(self, componentId, oldComponentStatus, newComponentStatus, incidentDetails:Incident):
        '''
        For now, if it's operational, close open incidents, and if it's not operational, create a new 
        ticket if one isn't already open for this component.  Future state will involve more detail around outage and maintenance
        '''
        incidentResult = IncidentResult()

        result = self.client.getUnresolvedIncidents()

        logger.debug(result)

        associatedIncidents = list(self.filter_set(result, componentId))
        asscIncidentCount = len(associatedIncidents)

        logger.info("Associated Incidents for %s: %d", componentId, asscIncidentCount)

        if (newComponentStatus == "operational"):
            if (asscIncidentCount > 0):
                for incident in associatedIncidents:
                    self.closeIncident(incident.id)
                    incidentResult.incidentResolved = True
                
        elif (newComponentStatus == "major_outage"):
            if (asscIncidentCount == 0):
                self.createIncident(componentId, newComponentStatus, incidentDetails)
                incidentResult.incidentCreated = True
        
        return incidentResult

    def closeIncident(self, incidentId):
        logger.info("Closing incident %s", incidentId)
        payload = { "incident": { "status": "resolved" } }
        self.client.updateIncident(incidentId, payload)

    def createIncident(self, componentId, newComponentStatus: str, incidentDetails: Incident):
        logger.info("Creating incident: Component %s - New Component Status %s", componentId, newComponentStatus)
        payload = { "incident": 
            {
                "name": incidentDetails.name,
                "status": "investigating",
                "body": incidentDetails.description,
                "component_ids": [ componentId ],
                "components": { componentId: newComponentStatus }
            }
        }
        self.client.createIncident(payload)