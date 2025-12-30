# Python Site Monitoring

![GitHub](https://img.shields.io/github/license/spydersoft-consulting/pi-monitor)
![GitHub release (with filter)](https://img.shields.io/github/v/release/spydersoft-consulting/pi-monitor)
![GitHub issues](https://img.shields.io/github/issues/spydersoft-consulting/pi-monitor)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/spydersoft-consulting/pi-monitor/build.yml)
![Sonar Violations (long format)](https://img.shields.io/sonar/violations/spydersoft-consulting_md_to_conf?server=https%3A%2F%2Fsonarcloud.io)

This tool can be used to monitor websites on a Raspberry Pi or other low-powered environment running Python.

## Usage

Please see the [Getting Started](https://spydersoft-consulting.github.io/pi-monitor/getting-started/) documentation for information on using this tool.

## Contributing

Please see the [Contribute](https://spydersoft-consulting.github.io/pi-monitor/contributing/) section of the documentation for information on development and contribution guidelines.

## Change Log

[Change Log](https://spydersoft-consulting.github.io/pi-monitor/changes/)

## Raspberry Pi install notes

`spydersoft-pi-monitor` includes optional SendGrid email support which depends on the `cryptography` package. On Raspberry Pi the latest `cryptography` may require building from source (Rust toolchain + maturin). To avoid surprises when installing on a Pi, follow the steps below.

- Install system build deps and modern Rust toolchain:

```bash
sudo apt update
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev pkg-config
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
rustup update stable
rustup default stable
```

- Install maturin and then install the package with the SendGrid extra:

```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install --user --upgrade maturin
export PATH="$HOME/.local/bin:$PATH"
python3 -m pip install spydersoft-pi-monitor[sendgrid]
```

If you do not need SendGrid you can install the package without the extra and `cryptography` will not be pulled in:

```bash
python3 -m pip install spydersoft-pi-monitor
```
