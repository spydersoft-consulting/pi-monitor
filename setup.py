#!/usr/bin/env python
from setuptools import setup
from pathlib import Path

if Path("version.txt").is_file():
    with open("version.txt") as f:
        version = f.read()
else:
    version = "0.0.0"

version_name = version.strip().lstrip("v")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="spydersoft-pi-monitor",
    version=version_name,
    description="Simple Python Website Monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Spydersoft Consulting",
    url="https://github.com/spydersoft-consulting/md_to_conf",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["pi_monitor"],
    install_requires=["pyyaml", "requests", "coloredlogs"],
    extras_require={
        "sendgrid": ["sendgrid"],
    },
    entry_points="""
    [console_scripts]
    pi-monitor=pi_monitor:main
    """,
    packages=["pi_monitor"],
    package_data={},
    include_package_data=False,
)
