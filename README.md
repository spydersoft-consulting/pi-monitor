<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Code Climate][codeclimate-shield]][codeclimate-url]


<!-- PROJECT LOGO -->
<br />
<p>
  <h3>PI Monitoring</h3>

  <p>
    Scripts for monitoring site uptime and reporting to statuspage.io
    <br />
    <br />
    <a href="https://github.com/spyder007/pi-monitoring/issues">Report Bug</a>
    ·
    <a href="https://github.com/spyder007/pi-monitoring/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

PI Monitoring is a set of Python scripts used to monitor web sites and report incidents and operational status to statuspage.io


### Built With

* [Python](https://www.python.org/)


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

* [Python](https://www.python.org/)
* [PyYaml]()
* [ColoredLogs]()

These scripts were written and tested on Python 3.7.3 (Raspbian) and 3.9.1 (Windows).  Install the dependencies as follows:
```sh
pip3 install pyyaml coloredlogs
```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/spyder007/pi-monitoring.git
   ```
2. Copy *.config.json.template files to *.config.json and modify the settings within those config files accordingly

3. Execute `monitor.py`
   ```sh
   python monitor.py
   ```

<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

## Configuration Settings

### Monitor (monitor.config.json)

`monitor.config.json` is a required configuration file that defines the checks to be executed.  See the table below for details.

```json
{
    "statusChecks": [...]
}
```

| Element | Description | Required? |
| ------- | ----------- | --------- |
| *statusChecks* | array of *[statusCheck](#StatusCheck)* objects | Yes |

### Notifications (notifications.config.json)

`notifications.config.json` is a required configuration file that defines settings for sending email notifications directly from the scripts.  See the table below for details.

> If this file is missing, notifications will not be sent via email

| Attribute | Description | Required? |
| ------- | ----------- | ---------| 
| smtp_url | Host/IP of the SMTP Server | Yes |
| smtp_port | SMTP Port for Host | Yes |
| smtp_sender_id | SMTP User Id | Yes |
| smtp_sender_pass | SMTP Password | Yes |
| smsEmail | Email to send notifications | Yes | 

> If you are using Gmail to send, you need to set your account's `Allow Less Secure Apps` setting to `true`

### StatusPage.io (statuspage_io.config.json)

`statuspage_io.config.json` is a required configuration file that defines settings for reporting incidents and component updats to statuspage.io.  See the table below for details.

| Attribute | Description | Required? |
| ------- | ----------- | ---------| 
| apiKey | API Key for statuspage.io | Yes |
| pageId | Page ID for statuspage.io | Yes |

## Object Definitions

### StatusCheck

A `statusCheck` represents a simple request to the defined `url`. If a non-200 the request generates an exception or a non-200 response, the site is determined to be down.  

If `statusPageComponentId` is defined, statuspage.io will be updated according to the following rules.

- If the site returns a 2xx response and statuspage.io lists the component as non-operational:
    - The component's status will be set to operational
    - Any open incidents associated with this component will be marked as resolved
- If the site returns a non-2xx response or an exception and statuspage.io lists the component as operational:
    - The component's status will be set to operational
    - An incident will be opened using the `name` and associated with this component.


```json
{
    "name": "Site name",
    "url": "https://my.domain.com/",
    "statusPageComponentId": "11111111"
}
```
| Attribute | Description | Required? |
| ------- | ----------- | ---------| 
| name | Name of the site being checked | Yes |
| url | URL to be retrieved for status check | Yes |
| statusPageComponentId | ComponentId for statuspage.io | No |

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/spyder007/pi-monitoring/issues) for a list of proposed features (and known issues).


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Matt Gerega - geregam@gmail.com

Project Link: [https://github.com/spyder007/pi-monitoring](https://github.com/spyder007/pi-monitoring)



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/spyder007/pi-monitoring.svg?style=for-the-badge
[contributors-url]: https://github.com/spyder007/pi-monitoring/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/spyder007/pi-monitoring.svg?style=for-the-badge
[forks-url]: https://github.com/spyder007/pi-monitoring/network/members
[stars-shield]: https://img.shields.io/github/stars/spyder007/pi-monitoring?style=for-the-badge
[stars-url]: https://github.com/spyder007/pi-monitoring/stargazers
[issues-shield]: https://img.shields.io/github/issues/spyder007/pi-monitoring.svg?style=for-the-badge
[issues-url]: https://github.com/spyder007/pi-monitoring/issues
[license-shield]: https://img.shields.io/github/license/spyder007/pi-monitoring.svg?style=for-the-badge
[license-url]: https://github.com/spyder007/pi-monitoring/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/geregam
[codeclimate-shield]: https://img.shields.io/codeclimate/maintainability/spyder007/pi-monitoring?style=for-the-badge
[codeclimate-url]: https://codeclimate.com/github/spyder007/pi-monitoring