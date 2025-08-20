#!/bin/bash

echo "Starting Airplanes Live Home Assistant Add-on"

# Start the web interface in the background
python3 /app/app.py &

# Start the MQTT service in the foreground
python3 /app/run.py