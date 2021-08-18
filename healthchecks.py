import requests
import logging
import statuspage_io
import notifications
from time import sleep

logger = logging.getLogger(__name__)
class StatusResult:
    success = True
    message = ''

    def __init__(self, success):
        self.success = success

def execute_status_check(statusCheckDef):

    operator = statuspage_io.StatusPageOperator()
       
    logger.info('Checking %s...', statusCheckDef['name'])
    incident = statuspage_io.Incident()
    sendNotification = False
    newComponentStatus = "operational"

    url = statusCheckDef['url']
    if (not url):
        logger.warn("Status Check %s contains no url", statusCheckDef['name'])
        return

    try:
        logger.info("Requesting %s", url)
        r = requests.get(url)
        logger.debug("Result: %s", r.text)
        statusResult = StatusResult(r.status_code == 200)
        if (not statusResult.success):
            logger.info("Request failed with Response Code %d: %s", r.status_code, r.text)
            statusResult.message = str.format("{0} {1}", r.status_code, r.text)
    except Exception as e:
        logger.error("Request failed exception %s", e)
        statusResult = StatusResult(False)
        statusResult.message = "Unknown status failure"

    if (statusResult.success):
        # Good Check
        logger.info("Status OK")
        newComponentStatus = "operational"

    else:
        # Bad check
        newComponentStatus = "major_outage"
        logger.warning(statusResult.message)
        incident.name = statusCheckDef['name']
        incident.description = str.format("{0} is not responsive", statusCheckDef['name'])
        sendNotification = True
    

    if (statusCheckDef['statusPageComponentId'] != ''):
        statusIoResult = operator.checkAndUpdateComponentStatus(statusCheckDef['statusPageComponentId'], newComponentStatus, incident)   
        sendNotification = statusIoResult.incidentResult.incidentCreated

    if (sendNotification):              
        notifications.notify(incident.name, incident.description) 



