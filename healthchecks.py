import configuration
import requests
import logging
import statuspage_io
import notifications
from time import sleep
from types import SimpleNamespace
from enums import OpLevel

logger = logging.getLogger(__name__)

class HttpGetResult:
    success: bool = True
    message: str = ''
    response: any = {}

    def __init__(self, success: bool, msg: str = ''):
        self.success = success
        self.message = msg
class HealthCheckExecutor:
    statuspage_operator: statuspage_io.StatusPageOperator
    notifier: notifications.Notifier

    def __init__(self, statusOperator: statuspage_io.StatusPageOperator, notifier: notifications.Notifier):
        self.statuspage_operator = statusOperator
        self.notifier = notifier

    def execute_status_check(self, checkSettings: configuration.CheckSettings):

        logger.info('Checking %s...', checkSettings.name)
        
        sendNotification = False
        opLevel = OpLevel.Operational

        httpResult = self.get_http(checkSettings.url)

        if (httpResult.success):
            # Good Check
            logger.info("Status OK")
            opLevel = OpLevel.Operational
        else:
            # Bad check
            opLevel = OpLevel.Full_Outage
            logger.warning(httpResult.message)
            sendNotification = True

        if (checkSettings.statusPage and checkSettings.statusPage.componentId != ''):
            statusIoResult = self.updateStatusPage(checkSettings, opLevel)
            sendNotification = statusIoResult.incidentResult.incidentCreated

        if (sendNotification):              
            self.notifier.notify(checkSettings.name, str.format("{0} is not responsive", checkSettings.name)) 

    def get_http(self, url: str) -> HttpGetResult:
        if (not url or url == ""):
            result = HttpGetResult(False, "no url defined")
            return result

        try:
            logger.info("Requesting %s", url)
            r = requests.get(url)
            result = self.process_response(r)
        except Exception as e:
            logger.error("Request failed exception %s", e)
            result = HttpGetResult(False, "Unknown status failure")

        return result

    def process_response(self, r: requests.Response) -> HttpGetResult:
        result = HttpGetResult(r.status_code == 200)
        if (not result.success):
            logger.info("Request failed with Response Code %d: %s", r.status_code, r.text)
            result.message = str.format("{0} {1}", r.status_code, r.text)
            return result
        
        result.rawResponse = r.text
        try:
            result.response = r.json(object_hook=lambda d: SimpleNamespace(**d))
        except:
            result.response = {}
        return result

    def updateStatusPage(self, checkSettings: configuration.CheckSettings, opLevel: OpLevel) -> statuspage_io.StatusResult:
        incident = statuspage_io.Incident()
        incident.name = checkSettings.name
        incident.description = str.format("{0} is not responsive", checkSettings.name)
        return self.statuspage_operator.checkAndUpdateComponentStatus(checkSettings.statusPage.componentId, opLevel, incident)   
        