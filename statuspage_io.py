import logging
import statuspage_io_client
import configuration
from enums import OpLevel

logger = logging.getLogger(__name__)


class Incident:
    """Incident Class

    This class represents the details about a Statuspage.io incident

    Attributes:
        name: The incident name.
        description: The incident description.

    """
    name: str = "Incident Name"
    description: str = "Incident Description"


class IncidentResult:
    """IncidentResult Class

    This class represents information about incidents created or resolved as part of a status change

    Attributes:
        incidentCreated: True if an incident was created, false otherwise.
        incidentResolved: True if an incident was created, false otherwise.

    """
    incidentCreated: bool = False
    incidentResolved: bool = False
    incident: Incident

    def __init__(self):
        self.incidentCreated = False
        self.incidentResolved = False
        self.incident = Incident()


class StatusResult:
    """StatusResult Class

    This class represents information about actions taken during a check and update.

    Attributes:
        statusChanged: True if the status has changed from the previous check, false otherwise.
        incidentResult: An instance of [IncidentResult][statuspage_io.IncidentResult].

    """
    statusChanged: bool = False
    incidentResult: IncidentResult = IncidentResult()

    def __init__(self):
        self.incidentResult = IncidentResult()


class StatusPageOperator:
    """StatusResult Class

    This class represents information about actions taken during a check and update.

    Attributes:
        config: An instance of [StatusPageSettings][configuration.StatusPageSettings] which contains settings for Statuspage.io communication 
        client: An instance of [StatusPageClient][statuspage_io_client.StatusPageClient], built from the configuration values provided.

    """

    config: configuration.StatusPageSettings = configuration.StatusPageSettings()
    client: statuspage_io_client.StatusPageClient

    def __init__(self, statusPageConfig: configuration.StatusPageSettings):
        """ Constructor

        Initialize the instance using the provided [StatusPageSettings][configuration.StatusPageSettings].

        """
        self.config = statusPageConfig
        self.client = statuspage_io_client.StatusPageClient(
            self.config.apiKey, self.config.pageId)

    def IsConfigured(self) -> bool:
        """ Validate configuration data

        Returns:
            True if the operator has a valid configuration, False otherwise.
        """
        return self.config.apiKey != ""

    def UpdateComponentStatus(self, componentId: str, opLevel: OpLevel, incidentDetails: Incident = {}) -> StatusResult:
        """ Update Component Status

        Using the provided OpLevel, determine the component's statuspage.io status. 

        If the incoming `opLevel` is [Operational][enums.OpLevel] and the statuspage.io status is not, the component's status will be changed to `operational`, and any open incidents for that component will be resolved.

        If the incoming `opLevel` is any other value and the statuspage.io status is operational, the component's status will be changed to `major_outage` and an incident will be created using the provided `incidentDetails`


        Args:
            componentId: The component ID to check
            opLevel: The current OpLevel for the provided component
            incidentDetails: An instance of [Incident][statuspage_io.Incident] which has the details of the incident to be created, if necessary.

        Returns:
            An instance of [StatusResult][statuspage_io.StatusResult]
        """

        if opLevel == OpLevel.Operational:
            componentStatus = "operational"
        else:
            componentStatus = "major_outage"

        if (componentStatus not in self.client.component_status_list):
            raise ValueError(str.format(
                "Invalid status '{0}'.  Valid values are {1}", componentStatus, self.client.component_status_list))

        result = StatusResult()
        component = self.client.getComponent(componentId)

        if (component.status != componentStatus and component.status != 'under_maintenance'):
            result.statusChanged = True
            logger.info("Changing status from %s to %s",
                        component.status, componentStatus)
            self._updateComponentStatus(componentId, componentStatus)
            result.incidentResult = self._processIncidentOnStatusChange(
                componentId, componentStatus, incidentDetails)

        return result

    def _updateComponentStatus(self, componentId, newComponentStatus):
        if (newComponentStatus not in self.client.component_status_list):
            raise ValueError(str.format(
                "Invalid status '{0}'.  Valid values are {1}", newComponentStatus, self.client.component_status_list))

        logger.debug("Setting component status to %s: %s",
                     newComponentStatus, componentId)
        payload = {"component": {"status": newComponentStatus}}
        self.client.updateComponent(componentId, payload)

    def _filter_set(self, incidents, componentId):
        def iterator_func(incident):
            for comp in incident.components:
                if comp.id == componentId:
                    return True
            return False

        return filter(iterator_func, incidents)

    def _getAssociatedIncident(self, componentId):
        result = self.client.getUnresolvedIncidents()
        return list(self._filter_set(result, componentId))

    def _processIncidentOnStatusChange(self, componentId: str, newComponentStatus: str, incidentDetails: Incident) -> IncidentResult:
        ''' Create or Close incidents based on the incoming component status

        For now, if it's operational, close open incidents, and if it's not operational, create a new 
        ticket if one isn't already open for this component.  Future state will involve more detail around outage and maintenance
        '''
        incidentResult = IncidentResult()
        incidentResult.incident = incidentDetails
        
        associatedIncidents = self._getAssociatedIncident(componentId)
        asscIncidentCount = len(associatedIncidents)
        logger.info("Associated Incidents for %s: %d",
                    componentId, asscIncidentCount)

        if (newComponentStatus == "operational" and asscIncidentCount > 0):
            for incident in associatedIncidents:
                self._closeIncident(incident.id)
                incidentResult.incidentResolved = True

        elif (newComponentStatus == "major_outage" and asscIncidentCount == 0):
            self._createIncident(
                componentId, newComponentStatus, incidentDetails)
            incidentResult.incidentCreated = True

        return incidentResult

    def _closeIncident(self, incidentId):
        logger.info("Closing incident %s", incidentId)
        payload = {"incident": {"status": "resolved"}}
        self.client.updateIncident(incidentId, payload)

    def _createIncident(self, componentId, newComponentStatus: str, incidentDetails: Incident):
        logger.info("Creating incident: Component %s - New Component Status %s",
                    componentId, newComponentStatus)
        payload = {"incident":
                   {
                       "name": incidentDetails.name,
                       "status": "investigating",
                       "body": incidentDetails.description,
                       "component_ids": [componentId],
                       "components": {componentId: newComponentStatus}
                   }
                   }
        self.client.createIncident(payload)
