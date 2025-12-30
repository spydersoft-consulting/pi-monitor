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

### Raspberry Pi install notes

If you want SendGrid email support the package requires a modern `cryptography` which may need to be built from source on Raspberry Pi. The steps below will install required system build tools and a Rust toolchain used by `maturin` (the build front-end) so the wheel can be built if a prebuilt wheel is not available.

1. Install system build dependencies and Rust:

```bash
sudo apt update
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev pkg-config
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
rustup update stable
rustup default stable
```

2. Install `maturin` and then the package with the `sendgrid` extra:

```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install --user --upgrade maturin
export PATH="$HOME/.local/bin:$PATH"
python3 -m pip install spydersoft-pi-monitor[sendgrid]
```

If you do not need SendGrid you can avoid this entirely and install without the extra:

```bash
python3 -m pip install spydersoft-pi-monitor
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
