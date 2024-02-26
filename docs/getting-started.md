# Getting Started

To get a local copy up and running follow these simple steps.

## Prerequisites

* [Python](https://www.python.org/)
* [PyYaml]()
* [ColoredLogs]()

These scripts were written and tested on Python 3.7.3 (Raspbian) and 3.9.1 (Windows).  Install the dependencies as follows:
```sh
pip3 install pyyaml coloredlogs
```

## Installation

1. Clone the repo
   ```sh
   git clone https://github.com/spyder007/pi-monitoring.git
   ```
2. Copy `monitor.config.json.template` to `monitor.config.json` and modify the settings within those config files accordingly

3. Execute `monitor.py`
   ```sh
   python monitor.py
   ```

## Configuration

1. Copy `monitor.config.json.template` to `monitor.config.json`.
2. Edit `monitor.config.json`.  Full documentation can be found in [Configuration][configuration]
``` json
{
    "status_checks": [
        {
            "name": "Site (Prod)",
            "url": "https://your.domain.com",
            "statusPageComponentId": "123215125"
        }
    ],
    "notification": {
        "smtp_url": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_sender_id": "gmail_email",
        "smtp_sender_pass": "gmail_pass",
        "sms_email": "email@vtext.com"
    },
    "statusPage": {
        "apiKey": "status_page_api_key",
        "pageId": "status_page_page_id"
    }
}
```