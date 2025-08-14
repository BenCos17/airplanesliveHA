# Airplanes Live API Add-on Documentation

## Overview
The Airplanes Live API Add-on integrates with [airplanes.live](https://airplanes.live) to provide real-time aircraft tracking data in Home Assistant via MQTT. Supports both the free feeder API and the authenticated REST API for premium features.

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
- **API Type**: Choose between "feeder" (free) or "authenticated" (REST API)
- **API Key**: Your airplanes.live API key for authenticated access
- **Tracking Mode**: summary, detailed, or both

## API Types

### Feeder API (feeder)
- **Endpoint**: `https://api.airplanes.live/v2/point`
- **Features**: Basic aircraft data, position tracking
- **Limitations**: Basic filtering, limited data fields
- **Radius**: Uses kilometers

### Authenticated REST API (feeder key based)
- **Endpoint**: `https://rest.api.airplanes.live`
- **Features**: Advanced filtering, comprehensive data, military aircraft
- **Requirements**: API key from airplanes.live
- **Radius**: Automatically converts km to nautical miles
- **Advanced Filters**: Altitude ranges, aircraft types, military, PIA, LADD

## MQTT Topics

### Summary Data
- `airplanes/live/summary` - Summary statistics

### Individual Aircraft (Detailed Mode)
- `airplanes/live/aircraft/<hex>/state` - Individual aircraft data

### Discovery
- `homeassistant/sensor/airplanes_live_<attribute>/config` - Entity discovery

## API Data Fields

The addon processes these fields from airplanes.live API:

### Position & Movement
- **Position**: `lat`, `lon`, `alt_baro`, `track`
- **Speed**: `gs` (ground), `tas` (true air), `ias` (indicated)
- **Distance**: `dst` (distance in nautical miles - REST API only)
- **Direction**: `dir` (direction from center point - REST API only)

### Aircraft Information
- **Flight**: `flight`, `t` (type), `desc` (description), `r` (registration)
- **Operator**: `ownOp` (owner/operator)
- **Year**: `year` (manufacturing year)

### Weather & Environment
- **Wind**: `wd` (wind direction), `ws` (wind speed)
- **Temperature**: `oat` (outside air temperature)
- **Pressure**: `nav_qnh` (barometric pressure)

### Navigation & Systems
- **Squawk**: `squawk` (transponder code)
- **Navigation**: `nav_altitude_mcp`, `nav_heading`
- **Technical**: `mlat`, `tisb`, `messages`, `rssi`

## Advanced Filtering (REST API Only)

### Altitude Filters
- `&above_alt_baro=<altitude>` - Aircraft above specified altitude
- `&below_alt_baro=<altitude>` - Aircraft below specified altitude

### Aircraft Type Filters
- `&filter_type=<type1>,<type2>` - Specific ICAO aircraft types
- Examples: A321, B738, B77L

### Special Categories
- `&filter_mil` - Military aircraft only
- `&filter_pia` - PIA hex code aircraft
- `&filter_ladd` - LADD list aircraft

### Position Filters
- `&filter_with_pos` - Only aircraft with valid position data

## Installation

1. Add the repository to Home Assistant
2. Install "Airplanes Live API" addon
3. Configure your location and preferences
4. Choose API type (feeder or authenticated)
5. Add API key if using authenticated mode
6. Start the addon

## Troubleshooting

### Common Issues
- **No aircraft showing**: Check coordinates and radius
- **MQTT connection issues**: Verify broker settings
- **Entity naming conflicts**: Ensure clean configuration
- **API key errors**: Verify API key and type selection

### Log Analysis
- Check addon logs for detailed information
- Look for API response data
- Verify MQTT publishing status
- Check API type and authentication status

## Security

- **Security Rating**: 6/8 (Good)
- **Network Access**: Required for API and MQTT
- **System Access**: Minimal, non-privileged
- **Container**: Standard security model
- **API Keys**: Stored securely in addon configuration

## Development

- **Version**: 1.4.9
- **Base Image**: ghcr.io/hassio-addons/base:14.0.0
- **Architectures**: aarch64, amd64, armhf, armv7, i386
- **License**: MIT
- **API Support**: Both feeder and REST APIs

## Support

- **GitHub**: [BenCos17/airplanesliveHA](https://github.com/BenCos17/airplanesliveHA)
- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: See README.md for detailed usage instructions
- **API Documentation**: [airplanes.live REST API](https://airplanes.live/docs)

---

*Last updated: August 14, 2025*
*Maintainer: BenCos17*
*Powered by: airplanes.live*