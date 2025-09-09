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
- **Configurable parameters** for location, radius, and update intervals
- **Flexible tracking modes** - choose between summary statistics, detailed tracking, or both
- **Automatic entity creation** in Home Assistant for each detected aircraft
- **Improved error handling** and logging with configurable levels
- **Configuration validation** to prevent invalid settings

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
- **API URL**: airplanes.live API endpoint (default: https://api.airplanes.live/v2/point)
- **Tracking Mode**: Choose tracking level (default: summary)
  - **summary**: Summary statistics only (count, closest, highest, fastest)
  - **detailed**: Individual aircraft tracking with separate entities
  - **both**: Both summary and detailed tracking

### Feeder Monitoring (optional)

If you run a local feeder (e.g., readsb, dump1090-fa) that exposes a metrics JSON endpoint, you can have this add-on publish feeder health and performance metrics to MQTT.

- `feeder_monitor_enabled` (default: false)
- `feeder_stats_url` (default: http://127.0.0.1:8080/metrics.json)
- `feeder_monitor_interval` seconds (default: 30)

MQTT topics:
- Raw JSON: `airplanes/live/feeder/raw`
- Summary JSON (used by HA sensors): `airplanes/live/feeder/summary`

Home Assistant discovery sensors are automatically created for a few key metrics when enabled:
- Feeder Messages 1min: `last1min.messages`
- Feeder Strong Signals 1min: `last1min.local.strong_signals`
- Feeder Noise dBFS 1min: `last1min.local.noise`
- Feeder Gain dB: `gain_db`

## Installation

1. Add this repository to your Home Assistant instance
2. Install the "Airplanes Live API" add-on
3. Configure your location and preferences
4. Start the add-on

## Usage

### Home Assistant Integration

Once the add-on is running, it will automatically create sensor entities in Home Assistant based on your tracking mode selection:

#### Summary Mode (Default)
Creates a single device with these sensors:
- **Aircraft Count**: Total number of aircraft in range
- **Lowest Altitude Aircraft**: Flight and altitude of lowest aircraft
- **Closest Distance Aircraft**: Flight and distance in km
- **Highest Aircraft**: Flight and altitude in feet
- **Fastest Aircraft (Ground)**: Highest ground speed in knots
- **Fastest Aircraft (Air)**: Highest air speed in knots
- **Aircraft Types**: Unique aircraft types currently in range
- **Weather Conditions**: Wind and temperature summary
- **Last Update**: Timestamp of last data update

#### Detailed Mode
Creates individual entities for each aircraft including:
- **Altitude**: Aircraft altitude in feet
- **Speed**: Aircraft speed in knots
- **Track**: Aircraft heading in degrees
- **Flight Number**: Flight identifier
- **Aircraft Type**: ICAO aircraft type code
- **Registration**: Aircraft registration number
- **Position**: Latitude and longitude coordinates

#### Both Mode
Combines both summary and detailed tracking for comprehensive monitoring.

### MQTT Topics

The add-on publishes to the following MQTT topics:

#### Summary Data
- `airplanes/live/summary` - Summary statistics data

#### Individual Aircraft (Detailed Mode)
- `airplanes/live/aircraft/<hex>/state` - Individual aircraft state data
- `homeassistant/sensor/airplane_<hex>_info/config` - Home Assistant discovery messages

#### Discovery
- `homeassistant/sensor/airplanes_live_<attribute>/config` - Home Assistant discovery messages

## Troubleshooting

### Common Issues

1. **No aircraft showing**: Check your latitude/longitude coordinates and radius
2. **MQTT connection issues**: Verify MQTT broker is running and credentials are correct
3. **API errors**: Check the add-on logs for detailed error messages
4. **Configuration validation errors**: Ensure coordinates are within valid ranges

### Logs

The add-on now provides structured logging with different levels:
- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues that don't stop operation
- **ERROR**: Problems that affect functionality
- **CRITICAL**: Severe issues that prevent operation

Check the add-on logs in Home Assistant for detailed information about:
- API requests and responses
- MQTT connection status
- Aircraft data processing
- Configuration validation results

### Configuration Validation

The add-on automatically validates your configuration:
- Latitude must be between -90 and 90
- Longitude must be between -180 and 180
- Radius must be a positive number
- Update interval must be 1 second or greater

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/BenCos17/airplanesliveHA).

## License

This project is licensed under the MIT License.

## Changelog

### Version 1.4.0
- **NEW**: Added flexible tracking modes (summary, detailed, both)
- **IMPROVED**: Implemented proper logging system with configurable levels
- **IMPROVED**: Added comprehensive configuration validation
- **IMPROVED**: Enhanced error handling with specific exception types
- **IMPROVED**: Increased API timeout for better reliability
- **FIXED**: Improved type handling for aircraft data processing
- **FIXED**: Better error messages and logging for troubleshooting
