# Getting Started

## Requirements

* Python 3.9+
* PIP

## Installation

You can install this tool using `pip`:

```bash
# If Python3 is your default
pip install spydersoft-pi-monitor

# On Raspberry Pi, or where you have both Python 2 and 3 installed
pip3 install spydersoft-pi-monitor
```

## Usage

### Basic

The minimal execution is to run `pi-monitor` in a directory where there is a file called `monitor.config.json` formatted as described in the [Configuration](#configuration) section.

To specify a configuration file, use the `-c` or `--configfile` command line flag.

```sh
pi-monitor --configfile my.config.json
```

## Configuration

1. Create a file called `monitor.config.json`.
2. Edit `monitor.config.json`.

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
        "smtp_sender_apikey": "gmail_pass",
        "sms_email": "email@vtext.com"
    },
    "status_page": {
        "api_key": "status_page_api_key",
        "page_id": "status_page_page_id"
    }
}
```
