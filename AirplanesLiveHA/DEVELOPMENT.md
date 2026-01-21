# Development Guide

This guide helps developers understand the codebase and contribute improvements to the Airplanes Live API Add-on.

## Project Structure

```
AirplanesLiveHA/
├── run.py                 # Main application logic
├── config.yaml            # Add-on configuration schema
├── Dockerfile             # Container build instructions
├── requirements.txt       # Python dependencies
├── rootfs/                # S6 service files
│   └── etc/services.d/
│       └── airplanes_live_api/
│           ├── run        # Service startup script
│           └── finish     # Service cleanup script
├── translations/          # UI translations
│   └── en.yaml           # English translations
├── README.md              # User documentation
├── CHANGELOG.md           # Version history
├── TROUBLESHOOTING.md     # Troubleshooting guide
├── DEVELOPMENT.md         # This file
└── config.example.yaml    # Configuration examples
```

## Architecture Overview

### Core Components

1. **Configuration Management**: Loads and validates settings from Home Assistant
2. **API Client**: Fetches aircraft data from airplanes.live API
3. **MQTT Publisher**: Publishes data to MQTT broker for Home Assistant integration
4. **Data Processing**: Processes and transforms aircraft data
5. **Entity Discovery**: Creates Home Assistant entities via MQTT discovery

### Data Flow

```
API Request → Data Fetch → Processing → MQTT Publishing → Home Assistant
     ↓              ↓          ↓            ↓              ↓
  airplanes.live → JSON → Aircraft List → MQTT Topics → Entities
```

## Key Functions

### `load_config()`
- Loads configuration from `/data/options.json`
- Provides fallback defaults
- Handles file reading errors gracefully

### `validate_config()`
- Validates coordinate ranges
- Ensures numeric values are valid
- Prevents invalid configurations from starting

### `fetch_airplane_data()`
- Makes HTTP requests to airplanes.live API
- Handles various error conditions
- Returns structured aircraft data

### `publish_discovery()`
- Publishes MQTT discovery messages
- Creates Home Assistant sensor entities
- Groups entities under a single device

### `publish_summary_data()`
- Processes aircraft data for summary statistics
- Calculates count, closest, highest, fastest
- Publishes to summary MQTT topic

### `publish_individual_aircraft()`
- Creates individual entities for each aircraft
- Publishes detailed aircraft information
- Only active when tracking mode allows

## Configuration Options

### Required Fields
- `latitude`: Location latitude (-90 to 90)
- `longitude`: Location longitude (-180 to 180)
- `radius`: Search radius in kilometers

### Optional Fields
- `update_interval`: Data refresh frequency (seconds)
- `mqtt_broker`: MQTT broker address
- `mqtt_port`: MQTT broker port
- `mqtt_topic`: Base MQTT topic
- `mqtt_username`: MQTT authentication
- `mqtt_password`: MQTT authentication
- `api_url`: API endpoint URL
- `tracking_mode`: Data tracking level

### Tracking Modes
- `summary`: Summary statistics only
- `detailed`: Individual aircraft tracking
- `both`: Both summary and detailed

## Development Setup

### Prerequisites
- Python 3.8+
- Docker
- Home Assistant development environment

### Local Development
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `options.json` with test configuration
4. Run: `python run.py`

### Testing Configuration
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius": 50,
  "update_interval": 10,
  "mqtt_broker": "localhost",
  "mqtt_port": 1883,
  "mqtt_topic": "test/airplanes",
  "tracking_mode": "both"
}
```

## Code Style Guidelines

### Python
- Use type hints for function parameters and return values
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings for all functions

### Error Handling
- Use specific exception types when possible
- Log errors with appropriate log levels
- Provide meaningful error messages
- Handle errors gracefully without crashing

### Logging
- Use structured logging with levels
- Include context in log messages
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Adding New Features

### 1. Configuration
- Add new options to `config.yaml`
- Update schema validation in `validate_config()`
- Add translations in `translations/en.yaml`

### 2. Data Processing
- Extend `fetch_airplane_data()` for new data sources
- Add new processing functions as needed
- Update data structures and types

### 3. MQTT Publishing
- Create new publishing functions
- Update discovery messages
- Add new MQTT topics

### 4. Testing
- Test with various configurations
- Verify MQTT message format
- Check Home Assistant entity creation

## Common Patterns

### Configuration Loading
```python
def load_config():
    config_path = "/data/options.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        log("Configuration file not found, using defaults", "warning")
        return {}
```

### Error Handling
```python
try:
    # Operation that might fail
    result = some_operation()
except SpecificException as e:
    log(f"Specific error: {e}", "error")
    return None
except Exception as e:
    log(f"Unexpected error: {e}", "critical")
    return None
```

### MQTT Publishing
```python
def publish_data(client, topic, payload):
    try:
        client.publish(topic, json.dumps(payload), retain=True)
        log(f"Published to {topic}")
    except Exception as e:
        log(f"Failed to publish to {topic}: {e}", "error")
```

## Testing

### Unit Tests
- Test individual functions with mock data
- Verify error handling paths
- Test configuration validation

### Integration Tests
- Test with real API endpoints
- Verify MQTT message format
- Test Home Assistant integration

### Performance Tests
- Monitor memory usage
- Check CPU utilization
- Test with large datasets

## Deployment

### Building
```bash
docker build -t airplanes-live-api .
```

### Testing Container
```bash
docker run -it --rm airplanes-live-api
```

### Home Assistant Integration
1. Update version in `config.yaml`
2. Test with local Home Assistant instance
3. Update documentation
4. Create release

## Version Management

**Important**: When updating the add-on version, ensure all version references are synchronized across the following files:

- **config.yaml** - `version` field (line 3)
- **run.py** - `DEFAULT_ADDON_VERSION` constant (line 28)
- **Dockerfile** - `ARG ADDON_VERSION` (line 23)
- **DOCS.md** - Version field in Development section (line 206)
- **TROUBLESHOOTING.md** - Example log message version (line 159)
- **CHANGELOG.md** - Add new version entry at the top (historical entries should remain unchanged)


## Contributing

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Make changes following guidelines
4. Test thoroughly
5. Update documentation
6. Submit pull request

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Error handling is appropriate
- [ ] Logging is comprehensive
- [ ] Configuration is documented
- [ ] Tests pass
- [ ] Documentation is updated

## Troubleshooting Development Issues

### Common Problems
1. **Configuration not loading**: Check file permissions and JSON format
2. **MQTT connection fails**: Verify broker is running and accessible
3. **API errors**: Check network connectivity and endpoint validity
4. **Entity creation issues**: Verify MQTT discovery message format

### Debug Mode
Enable debug logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

### MQTT Testing
Use mosquitto client to test MQTT:
```bash
mosquitto_sub -h localhost -t "test/airplanes/#" -v
```

## Future Enhancements

### Potential Features
- Web interface for configuration
- Historical data storage
- Advanced filtering options
- Alert system for specific aircraft
- Integration with other aviation APIs
- Dashboard widgets
- Mobile app support

### Performance Improvements
- Async/await implementation
- Connection pooling
- Caching strategies
- Rate limiting
- Batch processing

### Monitoring
- Health check endpoints
- Performance metrics
- Error rate tracking
- Resource usage monitoring
