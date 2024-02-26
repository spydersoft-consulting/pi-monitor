import os
import yaml
import logging.config
import logging
import logging.handlers
import coloredlogs
import argparse
from .healthchecks import HealthCheckExecutor
from .configuration import (
    read_configuration,
    MonitorSettings,
    NotificationSettings,
    StatusPageSettings,
    HealthCheckSettings,
    StatusPageComponentSettings
)
from .notifications import Notifier
from .statuspage_io import StatusPageOperator
from concurrent.futures import ThreadPoolExecutor


def get_parser():
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "-c", "--configfile", help="Configuration File", default="monitor.config.json"
    )

    return PARSER


def setup_logging(
    default_path="logging.yaml", default_level=logging.INFO, env_key="LOG_CFG"
):
    """
    | **@author:** Prathyush SP
    | https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19
    | Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print("Error in Logging Configuration. Using default configs")
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print("Failed to load configuration file. Using default configs")


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = get_parser()
    args = parser.parse_args()

    logger.info("Reading Configuration File")
    config_data = read_configuration(args.configfile, MonitorSettings())

    notifier = Notifier(config_data.notification)
    status_page_operator = StatusPageOperator(config_data.status_page)
    healtch_check_executor = HealthCheckExecutor(status_page_operator, notifier)

    with ThreadPoolExecutor(max_workers=4) as executor:
        {
            executor.submit(
                healtch_check_executor.execute_health_check, statusCheck
            ): statusCheck
            for statusCheck in config_data.status_checks
        }
