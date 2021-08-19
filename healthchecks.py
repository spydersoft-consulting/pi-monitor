import requests
import logging
import statuspage_io
import notifications
from time import sleep
import json
from types import SimpleNamespace

logger = logging.getLogger(__name__)
class HttpGetResult:
    success: bool = True
    message: str = ''
    response: any = {}

    def __init__(self, success: bool, msg: str = ''):
        self.success = success
        self.message = msg

def execute_status_check(statusCheckDef):

    operator = statuspage_io.StatusPageOperator()
       
    logger.info('Checking %s...', statusCheckDef.name)
    incident = statuspage_io.Incident()
    sendNotification = False
    newComponentStatus = "operational"

    httpResult = get_http(statusCheckDef.url)

    if (httpResult.success):
        # Good Check
        logger.info("Status OK")
        newComponentStatus = "operational"
    else:
        # Bad check
        newComponentStatus = "major_outage"
        logger.warning(httpResult.message)
        incident.name = statusCheckDef.name
        incident.description = str.format("{0} is not responsive", statusCheckDef.name)
        sendNotification = True

    if (statusCheckDef.statusPageComponentId != ''):
        statusIoResult = operator.checkAndUpdateComponentStatus(statusCheckDef.statusPageComponentId, newComponentStatus, incident)   
        sendNotification = statusIoResult.incidentResult.incidentCreated

    if (sendNotification):              
        notifications.notify(incident.name, incident.description) 

def get_http(url: str) -> HttpGetResult:
    if (not url or url == ""):
        result = HttpGetResult(False, "no url defined")
        return result

    try:
        logger.info("Requesting %s", url)
        r = requests.get(url)
        result = HttpGetResult(r.status_code == 200)
        if (not result.success):
            logger.info("Request failed with Response Code %d: %s", r.status_code, r.text)
            result.message = str.format("{0} {1}", r.status_code, r.text)
        else:
            result.rawResponse = r.text
            try:
                result.response = r.json(object_hook=lambda d: SimpleNamespace(**d))
            except:
                result.response = {}
    except Exception as e:
        logger.error("Request failed exception %s", e)
        result = HttpGetResult(False, "Unknown status failure")

    return result

