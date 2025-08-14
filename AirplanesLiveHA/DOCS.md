# Airplanes Live API Add-on Documentation

## Overview
The Airplanes Live API Add-on integrates with [airplanes.live](https://airplanes.live) to provide real-time aircraft tracking data in Home Assistant via MQTT.

## Features

### Tracking Modes
- **Summary Mode**: 8 comprehensive sensors with aggregated data
- **Detailed Mode**: Individual aircraft tracking with separate entities
- **Both Mode**: Combines summary and detailed tracking

### Summary Sensors (Default Mode)
1. **Aircraft Count** - Total aircraft in range
2. **Closest Aircraft** - Flight number and altitude of lowest aircraft
3. **Highest Aircraft** - Maximum altitude in feet
4. **Fastest Aircraft (Ground)** - Highest ground speed in knots
5. **Fastest Aircraft (Air)** - Highest air speed in knots
6. **Aircraft Types** - All aircraft types currently in range
7. **Weather Conditions** - Wind direction, speed, and temperature
8. **Last Update** - Timestamp of last data update

### Detailed Mode Sensors
- Flight number, altitude, speed, track, position
- Individual entity for each aircraft detected
- Device grouping for better organization

## Configuration

### Required Settings
- **Latitude**: Your location (-90 to 90)
- **Longitude**: Your location (-180 to 180)
- **Radius**: Search radius in kilometers

### Optional Settings
- **Update Interval**: Data refresh frequency (seconds)
- **MQTT Broker**: MQTT broker address
- **MQTT Port**: MQTT broker port
- **MQTT Topic**: Base MQTT topic
- **MQTT Username/Password**: Authentication (optional)
- **API URL**: airplanes.live API endpoint
- **Tracking Mode**: summary, detailed, or both

## MQTT Topics

### Summary Data
- `airplanes/live/summary` - Summary statistics

### Individual Aircraft (Detailed Mode)
- `airplanes/live/aircraft/<hex>/state` - Individual aircraft data

### Discovery
- `homeassistant/sensor/airplanes_live_<attribute>/config` - Entity discovery

## API Data Fields

The addon processes these fields from airplanes.live API:
- **Position**: `lat`, `lon`, `alt_baro`, `track`
- **Speed**: `gs` (ground), `tas` (true air), `ias` (indicated)
- **Aircraft**: `flight`, `t` (type), `desc` (description), `r` (registration)
- **Weather**: `wd` (wind direction), `ws` (wind speed), `oat` (temperature)
- **Navigation**: `squawk`, `nav_altitude_mcp`, `nav_heading`

## Installation

1. Add the repository to Home Assistant
2. Install "Airplanes Live API" addon
3. Configure your location and preferences
4. Start the addon

## Troubleshooting

### Common Issues
- **No aircraft showing**: Check coordinates and radius
- **MQTT connection issues**: Verify broker settings
- **Entity naming conflicts**: Ensure clean configuration

### Log Analysis
- Check addon logs for detailed information
- Look for API response data
- Verify MQTT publishing status

## Security

- **Security Rating**: 6/8 (Good)
- **Network Access**: Required for API and MQTT
- **System Access**: Minimal, non-privileged
- **Container**: Standard security model

## Development

- **Version**: 1.4.7
- **Base Image**: ghcr.io/hassio-addons/base:14.0.0
- **Architectures**: aarch64, amd64, armhf, armv7, i386
- **License**: MIT

## Support

- **GitHub**: [BenCos17/airplanesliveHA](https://github.com/BenCos17/airplanesliveHA)
- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: See README.md for detailed usage instructions

---

*Last updated: August 14, 2025*
*Maintainer: BenCos17*