
import json
from typing import List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StatusPageComponentSettings:
    """ Settings for StatusPage.io components

    """
    componentId: str


class Generic:
    @classmethod
    def from_dict(cls, dict):
        obj = cls()
        obj.__dict__.update(dict)
        return obj


class CheckSettings:
    """ Settings for HealthChecks

    Attributes:
        name (str): The name of the site being checked
        url (str): The url to be fetched as part of the check
        statusPage (StatusPageComponentSettings): Any StatusPage-related component settings
    """
    name: str
    url: str
    statusPage: StatusPageComponentSettings


class StatusPageSettings:
    """ Settings for StatusPage.io

    Attributes:
        apiKey (str): The API Key to access statuspage.io
        pageId (str): Your PageId for statuspage.io
    """
    apiKey: str
    pageId: str


class NotificationSettings:
    smtp_url: str
    smtp_port: int
    smtp_sender_id: str
    smpt_sender_pass: str
    smsEmail: str


class Settings:
    statusChecks: List[CheckSettings]
    notification: NotificationSettings
    statusPage: StatusPageSettings

    def __init__(self):
        pass


def readConfiguration(file: str = 'monitor.config.json', default: any = {}) -> Settings:
    configPath = Path(file)

    if (not configPath.exists()):
        logger.info("Configuration file not found: %s.  Using default", file)
        return default

    configDataRaw = configPath.read_text()
    return json.loads(configDataRaw, object_hook=Generic.from_dict)
