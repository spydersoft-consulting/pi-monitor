
import os
import yaml
import logging.config
import logging
import logging.handlers
import coloredlogs
import healthchecks
import configuration
import notifications
import statuspage_io
from concurrent.futures import ThreadPoolExecutor


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
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
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')


setup_logging()
logger = logging.getLogger(__name__)

logger.info("Reading Configuration File")
configData = configuration.readConfiguration("monitor.config.json", configuration.Settings())

notifier = notifications.Notifier(configData.notification)
statusPageOperator = statuspage_io.StatusPageOperator(configData.statusPage)
heathCheckExecutor = healthchecks.HealthCheckExecutor(statusPageOperator, notifier)

with ThreadPoolExecutor(max_workers=4) as executor:
    tasks = { executor.submit(heathCheckExecutor.execute_status_check, statusCheck): statusCheck for statusCheck in configData.statusChecks }