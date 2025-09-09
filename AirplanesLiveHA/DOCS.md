# Airplanes Live API Add-on Documentation

## Overview
The Airplanes Live API Add-on integrates with [airplanes.live](https://airplanes.live) to provide real-time aircraft tracking data in Home Assistant via MQTT. **Supports both the basic feeder API and the key-based REST API, but airplanes.live is transitioning to a stricter access model.** 

**⚠️ Policy Change Notice**: Airplanes.live has announced a shift to a "feeder access and request access model" due to abuse and commercial use policy violations. The basic feeder API will likely be removed in the future, requiring all users to use the authenticated REST API.

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
- **API Type**: Choose between "unauthenticated" (basic feeder) or "authenticated" (key-based REST API, also requires feeding)
- **API Key**: Your airplanes.live API key for authenticated access
- **Tracking Mode**: summary, detailed, or both

## API Types

### Feeder API (unauthenticated)
- **Endpoint**: `https://api.airplanes.live/v2/point`
- **Features**: Basic aircraft data, position tracking
- **Limitations**: Basic filtering, limited data fields
- **Radius**: Uses kilometers
- **Requirements**: Must contribute data to airplanes.live
- **Access**: Will be deprecated in favor of authenticated REST API

### Key-based REST API (authenticated)
- **Endpoint**: `https://rest.api.airplanes.live`
- **Features**: Advanced filtering, comprehensive data, military aircraft
- **Requirements**: API key from airplanes.live + must be a feeder + request access approval
- **Radius**: Automatically converts km to nautical miles
- **Advanced Filters**: Altitude ranges, aircraft types, military, PIA, LADD
- **Rate Limit**: 1 request per second
- **Access**: Requires approval and API key from airplanes.live

## Auto-Configuration

The addon automatically configures the correct API URL and radius format based on your `api_type` setting:

### Default Behavior
- **Feeder API**: Automatically uses `https://api.airplanes.live/v2/point` with kilometer radius
- **REST API**: Automatically uses `https://rest.api.airplanes.live` with nautical mile radius conversion

This prevents common configuration errors and ensures API compatibility.

### Disabling Auto-Configuration

If you need custom API endpoints or radius handling, you can disable auto-configuration:

```yaml
disable_auto_config: true
api_url: "https://your-custom-endpoint.com/api"
```

**⚠️ Important**: When auto-configuration is disabled:
- You're responsible for using the correct API endpoint format
- Radius units (km vs nautical miles) must be handled manually
- API compatibility and authentication headers are your responsibility
- The addon will use your exact `api_url` and `radius` settings without modification

**Recommendation**: Keep auto-configuration enabled unless you have specific custom requirements.

## MQTT Topics

### Summary Data
- `airplanes/live/summary` - Summary statistics

### Feeder Monitoring (optional)
- `airplanes/live/feeder/raw` - Raw feeder metrics JSON
- `airplanes/live/feeder/summary` - Same payload for HA sensors

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

## Getting API Access

**⚠️ Policy Change Notice**: Airplanes.live has announced stricter access requirements and will likely require all users to use the authenticated REST API in the future.

### Step 1: Request Access
1. **Contact Support**: Send a short description of your use case to [Airplanes.Live Support](https://airplanes.live/api-guide/)
2. **Join Discord**: Feel free to contact them in the [Airplanes.Live Discord](https://airplanes.live/api-guide/)
3. **Wait for Approval**: They will review your use case and grant access

### Step 2: Become a Data Feeder
- **Required**: You must contribute ADS-B data to airplanes.live
- **Setup**: Follow their [feeder setup guide](https://airplanes.live/api-guide/)
- **Hardware**: ADS-B receiver (RTL-SDR, FlightAware Pro Stick, etc.)

### Step 3: Get API Key (Optional)
- **For REST API**: Request an API key after feeder approval
- **For Basic API**: No key needed, just feeder status

## Installation

1. **Get API access approval** from airplanes.live (see above)
2. **Set up data feeding** to airplanes.live (required for both API types)
3. Add the repository to Home Assistant
4. Install "Airplanes Live API" addon
5. Configure your location and preferences
6. Choose API type (basic feeder or key-based REST API)
7. Add API key if using authenticated mode
8. Start the addon

## Troubleshooting

### Common Issues
- **No aircraft showing**: Check coordinates and radius
- **MQTT connection issues**: Verify broker settings
- **Entity naming conflicts**: Ensure clean configuration
- **API key errors**: Verify API key and type selection
- **403 Forbidden errors**: Check if you have API access approval from airplanes.live
- **No data from API**: Verify you're an active data feeder to airplanes.live

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

- **Version**: 1.4.29
- **Base Image**: ghcr.io/hassio-addons/base:14.0.0
- **Architectures**: aarch64, amd64, armhf, armv7, i386
- **License**: MIT
- **API Support**: Both feeder and REST APIs

## Support

- **GitHub**: [BenCos17/airplanesliveHA](https://github.com/BenCos17/airplanesliveHA)
- **My Discord server**: [discord](https://discord.gg/WW4eNQj9qr)

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: See README.md for detailed usage instructions
- **API Documentation**: [airplanes.live REST API](https://airplanes.live/api-guide/)

---

*Last updated: August 14, 2025*
*Maintainer: BenCos17*
*Powered by: airplanes.live*
