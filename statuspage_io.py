import json
import logging
import requests
import notifications

class Incident:
    name = "Incident Name"
    description = "Incident Description"


class StatusPageOperator:

    component_status_list = ['operational', 'under_maintenance', 'degraded_performance', 'partial_outage', 'major_outage']
    incident_status_list = ['investigating', 'identified', 'monitoring', 'resolved']
    scheduled_incident_status_list = ['scheduled', 'in_progress', 'verifying', 'complete']

    def __init__(self):
        self.config = self.getConfig()

    def getConfig(self):
        f = open('statuspage_io.config.json')
        configData = json.load(f)
        f.close()
        return configData

    def getHeaders(self):
        return {'Authorization': str.format('OAuth {0}', self.config['apiKey']), 'Content-Type': 'application/json'}

    def checkAndUpdateComponentStatus(self, componentId, componentStatus, incidentDetails: Incident=Incident()):
        if (componentStatus not in self.component_status_list):
            raise ValueError(str.format("Invalid status '{0}'.  Valid values are {1}", componentStatus, self.component_status_list))

        componentUrl = str.format("https://api.statuspage.io/v1/pages/{0}/components/{1}", self.config['pageId'], componentId)
        logging.debug(str.format("Retrieving component from StatusPage: {0}", componentUrl))
        component = requests.get(componentUrl, headers=self.getHeaders())
        componentJson = component.json()
        if (componentJson['status'] != componentStatus):
            logging.debug(str.format("Changing status from {0} to {1}", componentJson['status'], componentStatus))
            self.updateComponentStatus(componentId, componentStatus)
            self.checkAndLogIncident(componentId, componentJson['status'], componentStatus, incidentDetails)

        return True

    def updateComponentStatus(self, componentId, newComponentStatus):
        if (newComponentStatus not in self.component_status_list):
            raise ValueError(str.format("Invalid status '{0}'.  Valid values are {1}", newComponentStatus, self.component_status_list))

        componentUrl = str.format("https://api.statuspage.io/v1/pages/{0}/components/{1}", self.config['pageId'], componentId)
        logging.debug(str.format("Setting component status to {1}: {0}", componentUrl, newComponentStatus))
        payload = { "component": { "status": newComponentStatus } }
        r = requests.put(componentUrl, headers=self.getHeaders(), data=json.dumps(payload))


    def checkAndLogIncident(self, componentId, oldComponentStatus, newComponentStatus, incidentDetails:Incident):
        '''
        For now, if it's operational, close open incidents, and if it's not operational, create a new 
        ticket if one isn't already open for this component.  Future state will involve more detail around outage and maintenance
        '''
        unresolvedIncidentsUrl = str.format("https://api.statuspage.io/v1/pages/{0}/incidents/unresolved", self.config['pageId'])
        unresolvedIncidentsResponse = requests.get(unresolvedIncidentsUrl, headers=self.getHeaders())
        result = unresolvedIncidentsResponse.json()

        associatedIncidents = list(filter(lambda incident: incident['components'][0]['id'] == componentId, result))
        asscIncidentCount = len(associatedIncidents)

        if (newComponentStatus == "operational"):
            if (asscIncidentCount > 0):
                for incident in associatedIncidents:
                    logging.debug(str.format("Closing incident {0}", incident['id']))
                    self.closeIncident(incident['id'])
                
        elif (newComponentStatus == "major_outage"):
            if (asscIncidentCount == 0):
                self.createIncident(componentId, newComponentStatus, incidentDetails)

    def closeIncident(self, incidentId):
        incidentUrl = str.format("https://api.statuspage.io/v1/pages/{0}/incidents/{1}", self.config['pageId'], incidentId)
        logging.debug(str.format("Closing incident {1}: {0}", incidentUrl, incidentId))
        payload = { "incident": { "status": "resolved" } }
        r = requests.patch(incidentUrl, headers=self.getHeaders(), data=json.dumps(payload))

    def createIncident(self, componentId, newComponentStatus: str, incidentDetails: Incident):
        incidentUrl = str.format("https://api.statuspage.io/v1/pages/{0}/incidents", self.config['pageId'])
        logging.debug(str.format("Creating incident: {0}", incidentUrl))
        payload = { "incident": 
            {
                "name": incidentDetails.name,
                "status": "investigating",
                "body": incidentDetails.description,
                "component_ids": [ componentId ],
                "components": { componentId: newComponentStatus }
            }
        }
        r = requests.post(incidentUrl, headers=self.getHeaders(), data=json.dumps(payload))

        if (self.config['smsEmail'] != ''):
            notifications.notify(self.config['smsEmail'], incidentDetails.name, incidentDetails.description)