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