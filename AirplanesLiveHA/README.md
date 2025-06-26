# Home Assistant Add-on: Airplanes Live API

_Unofficial airplanes.live Home Assistant add-on_

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

## About

This add-on integrates with the [airplanes.live](https://airplanes.live) API to track live airplane data and expose it as Home Assistant entities via MQTT. It provides real-time aircraft information including position, altitude, speed, and flight details.

## Features

- **Real-time aircraft tracking** using the airplanes.live API
- **MQTT integration** for Home Assistant entity discovery
- **Web interface** with interactive map showing aircraft positions
- **Configurable parameters** for location, radius, and update intervals
- **Automatic entity creation** in Home Assistant for each detected aircraft

## Configuration

### Required Configuration

- **Latitude**: Your location's latitude (default: 53.2707)
- **Longitude**: Your location's longitude (default: -9.0568)
- **Radius**: Search radius in kilometers (default: 50)

### Optional Configuration

- **Update Interval**: How often to fetch new data in seconds (default: 10)
- **MQTT Broker**: MQTT broker address (default: core-mosquitto)
- **MQTT Port**: MQTT broker port (default: 1883)
- **MQTT Topic**: Base topic for MQTT messages (default: airplanes/live)
- **MQTT Username**: MQTT authentication username (optional)
- **MQTT Password**: MQTT authentication password (optional)

## Installation

1. Add this repository to your Home Assistant instance
2. Install the "Airplanes Live API" add-on
3. Configure your location and preferences
4. Start the add-on

## Usage

### Home Assistant Integration

Once the add-on is running, it will automatically create sensor entities in Home Assistant for each detected aircraft. These entities will include:

- **Altitude**: Aircraft altitude in feet
- **Speed**: Aircraft speed in knots
- **Track**: Aircraft heading in degrees
- **Flight Number**: Flight identifier
- **Aircraft Type**: ICAO aircraft type code
- **Registration**: Aircraft registration number

### Web Interface

Access the web interface at `http://your-home-assistant:8000` to see an interactive map showing all detected aircraft in real-time.

### API Endpoints

The add-on also provides REST API endpoints:

- `GET /api/airplanes` - Get all aircraft in the configured area
- `GET /api/airplane/<hex>` - Get specific aircraft by hex ID

## Troubleshooting

### Common Issues

1. **No aircraft showing**: Check your latitude/longitude coordinates and radius
2. **MQTT connection issues**: Verify MQTT broker is running and credentials are correct
3. **API errors**: Check the add-on logs for detailed error messages

### Logs

Check the add-on logs in Home Assistant for detailed information about:
- API requests and responses
- MQTT connection status
- Aircraft data processing

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/BenCos17/airplanesliveHA).

## License

This project is licensed under the Apache License 2.0.
