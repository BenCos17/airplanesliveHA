## 1.4.32
- Dynamic feeder metrics: auto-discover up to 200 sensors from stats.json
- Feeder discovery now also triggers on first stats publish
## 1.4.31
- Feeder discovery now published at startup and on first stats publish 
## 1.4.30
- Added feeder monitoring: fetch local feeder metrics, MQTT discovery for key stats, and publish raw/summary payloads
- Configurable from the add-on UI: `feeder_monitor_enabled`, `feeder_stats_url`, `feeder_monitor_interval`
- Documentation updated (README, DOCS)
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

 Version 1.4.10 Changes:
 - **FIXED**: Schema validation errors preventing addon from loading in Home Assistant
 - **FIXED**: Invalid 'select' type and 'api_type_options' array in config.yaml
 - **IMPROVED**: Changed api_type to use 'str' type for better Home Assistant compatibility
 - **ENHANCED**: Updated example configuration with new API fields

 Version 1.4.11 Changes:
 - **FIXED**: Critical bug where REST API was using wrong URL format causing 403 errors
 - **FIXED**: Variable scope error in logging when no aircraft data available
 - **IMPROVED**: Better error handling for 403 Forbidden responses with helpful messages
 - **ENHANCED**: Proper auto-configuration of API URLs based on selected type

 Version 1.4.12 Changes:
 - **NEW**: Added option to disable auto-configuration for advanced users
 - **NEW**: Added `disable_auto_config` configuration option
 - **IMPROVED**: Better logging for auto-configuration status
 - **ENHANCED**: Comprehensive documentation of auto-configuration behavior
 - **DOCS**: Added detailed auto-configuration section to DOCS.md

 Version 1.4.13 Changes:
 - **IMPROVED**: Changed API type terminology from "free" to "unauthenticated" for accuracy
 - **IMPROVED**: Changed "authenticated" to "key-based REST API" for clarity
 - **ENHANCED**: Updated all documentation to reflect correct terminology
 - **DOCS**: Clarified that feeder API requires data contribution to airplanes.live
 - **TRANSLATIONS**: Updated English translations with more accurate descriptions

 Version 1.4.14 Changes:
 - **CLARIFIED**: Both API types require data contribution to airplanes.live
 - **IMPROVED**: Updated documentation to emphasize feeder requirement for all users
 - **ENHANCED**: Better descriptions in translations and example configs
 - **DOCS**: Added clear notes about data contribution requirements throughout

 Version 1.4.15 Changes:
 - **UPDATED**: Documentation to reflect airplanes.live's new "feeder access and request access model"
 - **NEW**: Added comprehensive "Getting API Access" section with step-by-step instructions
 - **ENHANCED**: Updated requirements to include access approval from airplanes.live support
 - **IMPROVED**: Added troubleshooting for 403 errors and access issues
 - **DOCS**: Added official airplanes.live API guide links and contact information


 Version 1.4.16 Changes:
 - **UPDATED**: Documentation to assume basic feeder API will be deprecated in the future
 - **IMPROVED**: Clearer messaging about future authentication requirements

 Version 1.4.17 Changes:
 - **FIXED**: Last Update sensor now shows human-readable date format instead of ISO timestamp
 - **IMPROVED**: Changed from "2025-08-14T23:17:29.367421" to "2025-08-14 23:17:29"

 Version 1.4.18 Changes:
 - **NEW**: Added separate sensor for "Lowest Altitude Aircraft" (shows flight + altitude)
 - **NEW**: Added separate sensor for "Closest Distance Aircraft" (shows flight + distance in km)
 - **IMPROVED**: Replaced single "Closest Aircraft" sensor with two specialized sensors
 - **ENHANCED**: Now shows both altitude-based and geographic distance-based closest aircraft
 - **TECHNICAL**: Added Haversine formula for accurate distance calculations from your coordinates

 Version 1.4.19 Changes:
 - **FIXED**: Critical KeyError 'aircraft_types' crash when publishing summary data
 - **FIXED**: Missing 'aircraft_types' and 'weather' fields in summary payload for empty aircraft lists
 - **IMPROVED**: Enhanced API response logging with detailed structure information
 - **IMPROVED**: Better error handling and debugging for API responses
 - **ENHANCED**: Robust logging that won't crash on missing data fields
 - **TECHNICAL**: Added comprehensive debugging for API response structure and summary payload creation

 Version 1.4.20 Changes:
 - **IMPROVED**: Enhanced error handling for API response parsing
 - **FIXED**: Better handling of malformed aircraft data
 - **ENHANCED**: More robust summary data generation

 Version 1.4.21 Changes:
 - **IMPROVED**: Better logging for API response debugging
 - **ENHANCED**: Improved error messages for troubleshooting

 Version 1.4.22 Changes:
 - **FIXED**: API response field mapping from 'ac' to 'aircraft' for REST API compatibility
 - **NEW**: Added backward compatibility for legacy 'ac' field format (feeder API)
 - **IMPROVED**: Automatic detection of API response format (aircraft vs ac)
 - **ENHANCED**: Support for both feeder API ('ac') and REST API ('aircraft') formats
 - **TECHNICAL**: Universal API response handling with automatic fallback
 
 Version 1.4.23 Changes:
 - **FIXED**: Made api_key optional in configuration schema to prevent validation errors
 - **FIXED**: Configuration validation now properly handles missing api_key for unauthenticated API type
 - **IMPROVED**: Better schema validation for optional API key field
 - **ENHANCED**: Users can now save configuration without api_key when using feeder API

 Version 1.4.24 Changes:
 - **ENHANCED**: "Highest Aircraft" sensor now shows flight number and altitude (e.g., "ABC123 (35000ft)") instead of just altitude
 - **IMPROVED**: Better aircraft identification in summary sensors for easier tracking
 - **FIXED**: Consistent data format across all aircraft sensors (flight + data format)

 Version 1.4.25 Changes:
 - **IMPROVED**: Centralized version management - version number now read from config.yaml instead of hardcoded in multiple files
 - **ENHANCED**: Added PyYAML dependency for YAML configuration parsing
 - **TECHNICAL**: Single source of truth for version number across all addon components



 Version 1.4.28 Changes:
 - **NEW**: Complete MQTT system overhaul with robust connection management
 - **NEW**: Added MQTTManager class for better connection reliability and message queuing
 - **NEW**: Configurable MQTT QoS (0, 1, 2) and message retention settings
 - **IMPROVED**: Exponential backoff reconnection with configurable delays (1s to 5 minutes)
 - **IMPROVED**: Message queuing when disconnected - messages are sent when reconnected
 - **IMPROVED**: Last Will and Testament for automatic offline status when connection drops
 - **IMPROVED**: Heartbeat system for connection health monitoring every 30 seconds
 - **IMPROVED**: Better error handling with specific MQTT error code explanations
 - **IMPROVED**: Thread-safe connection management with connection locking
 - **ENHANCED**: MQTT status topic for monitoring add-on health and connection state
 - **ENHANCED**: Comprehensive MQTT statistics and connection monitoring
 - **ENHANCED**: Better Home Assistant integration with improved discovery reliability
 - **TECHNICAL**: Automatic message processing from queue on reconnection
 - **TECHNICAL**: Enhanced logging for MQTT operations and connection states

 Version 1.4.29 Changes:
 - **CHANGED**: Exposed MQTT QoS and retain as configurable options in add-on config
 - **FIXED**: Docker healthcheck now uses reliable process check
 - **CLEANUP**: Removed obsolete run.sh (web app removed previously)
 - **DOCS**: Updated sensors list and aligned documentation version