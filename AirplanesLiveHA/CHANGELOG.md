 Version 1.3.18 Changes:
 testing mqtt stuff to try and fix the config

 version 1.3.19 Changes: 
 more pain

 Version 1.3.20 Changes:
 - Fixed schema validation for latitude and longitude fields to use proper float range constraints
 - Updated schema format to float(-90.0,90.0) and float(-180.0,180.0) for Home Assistant compatibility

 Version 1.3.21 Changes:
 - Modified add-on to read configuration from Home Assistant options.json instead of hardcoded values
 - Removed hardcoded MQTT credentials - now configurable through add-on options
 - Updated both run.py and app.py to use centralized configuration loading
 - Improved user experience by making all settings configurable through Home Assistant UI

 Version 1.3.22 Changes:
 - Enhanced configuration following Home Assistant add-on best practices
 - Added URL link to GitHub repository for support and documentation
 - Added webui configuration for easy access to the web interface
 - Added watchdog URL for health monitoring
 - Added port descriptions for better user experience
 - Created English translation file with proper labels and descriptions for all configuration options
 - Improved add-on description to be more comprehensive and user-friendly

 Version 1.3.23 Changes:
 - Fixed web UI not working by starting Flask server alongside MQTT service
 - Added health check endpoint (/health) for reliable watchdog monitoring
 - Updated watchdog URL to use health endpoint instead of API endpoint
 - Both Flask web server and MQTT service now run simultaneously

 Version 1.3.24 Changes:
 - Fixed permission denied error when reading /data/options.json by removing USER directive from Dockerfile
 - Removed default MQTT credentials to prevent authentication conflicts
 - Users must now configure MQTT username and password through the add-on options
 - Improved compatibility with Home Assistant's default Mosquitto add-on

 Version 1.3.25 Changes:
 - Minor improvements and documentation updates

 Version 1.3.26 Changes:
 - Fixed Home Assistant MQTT discovery by removing invalid 'device_class: sensor' from discovery payloads
 - Entities now appear correctly in Home Assistant

 Version 1.3.27 Changes:
 - Each aircraft attribute (altitude, speed, track, flight, registration, type) is now published as a separate Home Assistant entity per aircraft
 - All entities for a given aircraft are grouped under a single device in Home Assistant

 Version 1.3.28 Changes:
 - Fixed web interface connection issues by properly configuring s6 service management
 - Updated web interface to use HTTP polling instead of MQTT WebSocket for better reliability
 - Improved service startup to run both web interface and MQTT service simultaneously
 - Enhanced web interface with better aircraft data display and real-time updates
 - Added comprehensive troubleshooting documentation for web interface issues
 - Updated README with accurate feature descriptions and usage instructions
 - Added health endpoint testing and improved error handling

 Version 1.3.29 Changes:
 - Removed web interface to simplify the addon and focus on MQTT functionality as it didn't work that well anyway 
 - Removed Flask dependencies and web-related configuration
 - Simplified service startup to only run MQTT service
 - Updated documentation to reflect MQTT-only functionality
 - Reduced addon complexity and potential points of failure

 Version 1.3.30 Changes:
 - Fixed container startup issue by using proper Home Assistant base image with s6-overlay support
 - Updated Dockerfile to use ghcr.io/hassio-addons/base:14.0.0
 - Fixed Alpine Linux compatibility with proper package installation
 - Ensured service files are properly copied and have correct permissions

 Version 1.3.31 Changes:
 - Fixed package conflict with musl-dev on i386 architecture
 - Removed problematic musl-dev package from Dockerfile
 - Simplified package installation to work across all architectures

 Version 1.3.32 Changes:
 - Removed all leftover/example services (example, airplanes_live_web) from the add-on
 - Cleaned up service directory to only include the main airplanes_live_api service
 - No more permission errors from unused or example services
 - Finalized cleanup for a production-ready, minimal, and error-free add-on

 Version 1.3.33 Changes:
 - MAJOR CHANGE: Switched from individual aircraft devices to single "Airplanes Live" device
 - Single device contains 5 summary sensors: Aircraft Count, Closest Aircraft, Highest Aircraft, Fastest Aircraft, Last Update
 - No cleanup needed - aircraft are able to come and go without creating permanent devices

 Version 1.3.34 Changes:
 - Fixed type comparison error when processing aircraft altitude and speed data
 - Added proper type conversion and error handling for string/number comparisons
 - Improved robustness when API returns mixed data types
 - Fixed "'<' not supported between instances of 'str' and 'int'" error

 Version 1.4.0 Changes:
 - **NEW**: Added flexible tracking modes (summary, detailed, both) for customizable aircraft monitoring
 - **IMPROVED**: Implemented proper logging system with configurable levels (INFO, WARNING, ERROR, CRITICAL)
 - **IMPROVED**: Added comprehensive configuration validation for coordinates, radius, and update intervals
 - **IMPROVED**: Enhanced error handling with specific exception types and better error messages
 - **IMPROVED**: Increased API timeout from 10 to 15 seconds for better reliability
 - **IMPROVED**: Added type hints throughout the codebase for better maintainability
 - **IMPROVED**: Better MQTT connection handling with improved retry logic
 - **FIXED**: Improved type handling for aircraft data processing to prevent runtime errors
 - **FIXED**: Better error messages and logging for easier troubleshooting
 - **FIXED**: Corrected bug in fastest aircraft calculation logic
 - **ENHANCED**: Individual aircraft tracking now creates proper Home Assistant entities with device grouping
 - **ENHANCED**: Added support for publishing individual aircraft data when detailed tracking is enabled

 Version 1.4.1 Changes:
 - **FIXED**: Docker build failure caused by pip cache purge command when cache is disabled
 - **IMPROVED**: Simplified Dockerfile pip installation commands for better reliability
 - **IMPROVED**: Maintained security improvements while fixing build issues

 Version 1.4.2 Changes:
 - **FIXED**: Schema validation errors preventing addon from loading in Home Assistant
 - **FIXED**: Invalid 'select' type and 'tracking_mode_options' array in config.yaml
 - **IMPROVED**: Changed tracking_mode to use 'str' type for better Home Assistant compatibility

 Version 1.4.3 Changes:
 - **FIXED**: Docker container permission issues with s6-overlay-suexec
 - **FIXED**: "unable to setgid to root: Operation not permitted" error
 - **IMPROVED**: Simplified Dockerfile user management for better compatibility

 Version 1.4.4 Changes:
 - **FIXED**: "max() arg is an empty sequence" error when processing aircraft data
 - **IMPROVED**: Added detailed logging for altitude and speed data processing
 - **IMPROVED**: Better error handling and debugging information for troubleshooting

 Version 1.4.5 Changes:
 - **NEW**: Added custom addon icon for better visual identification in Home Assistant

 Version 1.4.6 Changes:
 - **FIXED**: Speed sensors now properly read from airplanes.live API using correct field names
 - **NEW**: Added separate sensors for ground speed (gs) and air speed (tas/ias)
 - **NEW**: Added Aircraft Types sensor showing all aircraft types in range
 - **NEW**: Added Weather Conditions sensor showing wind and temperature data
 - **IMPROVED**: Better speed data processing with fallback to multiple speed fields
 - **ENHANCED**: Summary mode now shows 8 sensors with comprehensive aircraft data

 Version 1.4.7 Changes:
 - **FIXED**: Duplicate entity naming issue (e.g., "airplanes_live_airplanes_live_aircraft_types")
 - **IMPROVED**: Cleaner entity names without redundant prefixes
 - **ENHANCED**: Better organization and easier identification of sensors in Home Assistant

 Version 1.4.8 Changes:
 - **CHANGED**: Manufacturer from "airplanes.live" to "BenCos17" in device information to make it more clear it's not offical, add note about being powered by airplanes.live in also

 Version 1.4.9 Changes:
 - **NEW**: Added support for airplanes.live REST API with API key authentication
 - **NEW**: Added API type selection (feeder vs authenticated feeder)
 - **NEW**: Added API key configuration option for key based features
 - **IMPROVED**: Automatic radius conversion (km to nautical miles for REST API)
 - **ENHANCED**: Support for advanced filtering and more data with authenticated API 
