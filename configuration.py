
import json
from types import SimpleNamespace
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def readConfiguration(file: str, default: any = {}):
    configPath = Path(file)

    if (not configPath.exists()):
        logger.info("Configuration file not found: %s.  Using default", file)
        return default

    configData = configPath.read_text()
    return json.loads(configData, object_hook=lambda d: SimpleNamespace(**d))