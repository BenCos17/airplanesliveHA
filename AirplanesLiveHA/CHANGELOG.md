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