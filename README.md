# Airplanes Live API Add-on

This Home Assistant add-on fetches live airplane tracking data from the [Airplanes.Live API](https://airplanes.live/api-guide/) and publishes it to an MQTT broker for Home Assistant integration.

## Features

- **Real-time aircraft tracking** using the airplanes.live API
- **MQTT integration** for Home Assistant entity discovery
- **Configurable parameters** for location, radius, and update intervals

## Configuration

The add-on can be configured through the Home Assistant add-on interface with the following options:

- `api_url`: Base URL for the Airplanes.Live API (default: https://api.airplanes.live/v2/point)
- `latitude`, `longitude`, `radius`: The area to monitor (default: 53.2707, -9.0568, 50km)
- `update_interval`: How often to fetch new data in seconds (default: 10)  please respect the api limits and don't spam it though  [READ THIS](https://github.com/BenCos17/airplanesliveHA/blob/main/README.md#new-limits-after-01-dec-2025)

- `mqtt_broker`, `mqtt_port`, `mqtt_topic`: MQTT settings (default: core-mosquitto, 1883, airplanes/live)
- `mqtt_username`, `mqtt_password`: MQTT authentication (optional)

## Installation

1. Add this repository to your Home Assistant instance
2. Install the "Airplanes Live API" add-on
3. Configure your location and preferences
4. Start the add-on

## Usage

### Home Assistant Integration

Once running, the add-on automatically creates sensor entities in Home Assistant for each detected aircraft, including altitude, speed, track, flight number, aircraft type, and registration.

### MQTT Topics

The add-on publishes aircraft data to MQTT topics that Home Assistant can discover and integrate as entities.

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/BenCos17/airplanesliveHA).

## License

This project is licensed under the MIT License.

---

Add-on documentation: <https://developers.home-assistant.io/docs/add-ons>

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FBenCos17%2FairplanesliveHA)

## Add-ons

This repository contains the following add-on:

### [Airplanes Live API](./AirplanesLiveHA)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

_Real-time aircraft tracking addon for https://airplanes.live._

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg




#Note:
from the server 
 starting **__01 DEC 2025__**, we will be placing limits on the free API. This was not an easy decision to come to, but there were several factors. The most important were: 1) We want to encourage people to contribute, rather than using the data and not offering anything back to the community; 2) We want to ensure we set ourselves up to be sustainable in the future as we build out more features; and 3) There has been a significant increase in abuse, both by individuals and commercial entities (mostly commercial entities). Once the limits are in place, the number of requests you can make from the IP you contribute from will be increased automatically. In the future, you'll be able to get a key that you can use from anywhere. We will also be decommissioning the ADS-B One API because it serves the same data and purpose as the Airplanes.live API.

**__We will continue to provide API keys to app developers, journalists, academics, researchers, emergency services, etc. - just shoot us an email at ([contact@airplanes.live](mailto:contact@airplanes.live)) and request it. Those with an existing API key will NOT be impacted.__**
# **__New Limits After 01 DEC 2025__**:
## **__Free__**:
**500 requests per day.**
-# If split across the entire day, that's 1 request every ~180 seconds.

## **__Contributor__**:
**8,640 requests per day.** 
-# If split across the entire day, that's 1 request every 10 seconds.

-# **Note**: Rate limits are applied across the API, not per endpoint.
