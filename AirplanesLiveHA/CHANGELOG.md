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