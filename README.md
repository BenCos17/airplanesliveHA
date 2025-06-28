# Airplanes Live API Add-on

This Home Assistant add-on fetches live airplane tracking data from the [Airplanes.Live API](https://airplanes.live/api-guide/) and publishes it to an MQTT broker, while also providing a web interface and REST API endpoints.

## Features

- **Real-time aircraft tracking** using the airplanes.live API
- **MQTT integration** for Home Assistant entity discovery
- **Web interface** with interactive map showing aircraft positions
- **REST API endpoints** for programmatic access
- **Configurable parameters** for location, radius, and update intervals
- **Automatic entity creation** in Home Assistant for each detected aircraft

## Configuration

The add-on can be configured through the Home Assistant add-on interface with the following options:

- `api_url`: Base URL for the Airplanes.Live API (default: https://api.airplanes.live/v2/point)
- `latitude`, `longitude`, `radius`: The area to monitor (default: 53.2707, -9.0568, 50km)
- `update_interval`: How often to fetch new data in seconds (default: 10)
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

### Web Interface

Access the interactive map at `http://your-home-assistant:8000` to see real-time aircraft positions with detailed information in popup windows.

### API Endpoints

- `GET /api/airplanes` - Get all aircraft in the configured area
- `GET /api/airplane/<hex>` - Get specific aircraft by hex ID
- `GET /health` - Health check endpoint

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
