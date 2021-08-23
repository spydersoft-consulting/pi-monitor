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
    """HttpGetResult
    
    Attributes:
        success: Whether or not the request was successful
        message: The error message from an unsuccessful request
        rawResponse: The string value of the response body
        response: An object representing the response body converted as JSON

    """
    success: bool = True
    message: str = ''
    rawResponse: str
    response: any = {}

    def __init__(self, success: bool, msg: str = ''):
        self.success = success
        self.message = msg


class HealthCheckExecutor:
    """HealthCheckExecutor

    The HealthCheckExecutor encapsulates the functionality to perform a health check on a site and properly notify users or update statuspage.io accordingly.

    A Healthcheck represents a simple request to the defined `url`. If a non-200 the request generates an exception or a non-200 response, the site is determined to be down.  

    If `statuspage_operator` is present and the HealthCheckSettings have a componentId set, statuspage.io will be updated according to the following rules.

    - If the site returns a 2xx response and statuspage.io lists the component as non-operational:
        - The component's status will be set to operational
        - Any open incidents associated with this component will be marked as resolved
    - If the site returns a non-2xx response or an exception and statuspage.io lists the component as operational:
        - The component's status will be set to operational
        - An incident will be opened using the `name` and associated with this component.


    Attributes:
        statuspage_operator: The name of the site being checked
        notifier: The url to be fetched as part of the check
    """
    statuspage_operator: statuspage_io.StatusPageOperator
    notifier: notifications.Notifier

    def __init__(self, statusOperator: statuspage_io.StatusPageOperator, notifier: notifications.Notifier):
        """Constructor

        Constructs an instance of the HealthCheckExecutor with the given [StatusPageOperator][statuspage_io.StatusPageOperator] and [Notifier][notifications.Notifier].

        Attributes:
            statuspage_operator: The name of the site being checked
            notifier: The url to be fetched as part of the check
        """
        self.statuspage_operator = statusOperator
        self.notifier = notifier

    def execute_health_check(self, checkSettings: configuration.HealthCheckSettings):
        """ Execute a health check

        Executes a health check using the provided HealthCheckSettings.

        Args:
            checkSettings: An instance of [HealthCheckSettings][configuration.HealthCheckSettings]
        """
        logger.info('Checking %s...', checkSettings.name)

        sendNotification = False
        opLevel = OpLevel.Operational

        httpResult = self._get_http(checkSettings.url)

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
            statusIoResult = self._updateStatusPage(checkSettings, opLevel)
            sendNotification = statusIoResult.incidentResult.incidentCreated

        if (sendNotification):
            self.notifier.notify(checkSettings.name, str.format(
                "{0} is not responsive", checkSettings.name))

    def _get_http(self, url: str) -> HttpGetResult:
        """ Retrieve data from the URL

        Attempt to get data from the provided URL

        Args:
            url: The url to be retrieved

        Returns:
            An [HttpGetResult][healthchecks.HttpGetResult]
        """
        if (not url or url == ""):
            result = HttpGetResult(False, "no url defined")
            return result

        try:
            logger.info("Requesting %s", url)
            r = requests.get(url)
            result = self._process_response(r)
        except Exception as e:
            logger.error("Request failed exception %s", e)
            result = HttpGetResult(False, "Unknown status failure")

        return result

    def _process_response(self, response: requests.Response) -> HttpGetResult:
        """ Process the HTTP Requests response

        Convert the provided Response object from the requests module into an [HttpGetResult][healthchecks.HttpGetResult]. 

        Args:
            response: The [requests.Response] object from the HTTP operation

        Returns:
            An [HttpGetResult][healthchecks.HttpGetResult]
        """
        result = HttpGetResult(response.status_code == 200)
        if (not result.success):
            logger.info("Request failed with Response Code %d: %s",
                        response.status_code, response.text)
            result.message = str.format("{0} {1}", response.status_code, response.text)
            return result

        result.rawResponse = response.text
        try:
            result.response = response.json(
                object_hook=lambda d: SimpleNamespace(**d))
        except:
            result.response = {}
        return result

    def _updateStatusPage(self, checkSettings: configuration.HealthCheckSettings, opLevel: OpLevel) -> statuspage_io.StatusResult:
        incident = statuspage_io.Incident()
        incident.name = checkSettings.name
        incident.description = str.format(
            "{0} is not responsive", checkSettings.name)
        return self.statuspage_operator.UpdateComponentStatus(checkSettings.statusPage.componentId, opLevel, incident)
