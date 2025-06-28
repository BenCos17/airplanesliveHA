#!/usr/bin/with-contenv bashio

echo "Starting Airplanes Live Home Assistant Add-on"

# Start the Flask web server in the background
echo "Starting Flask web server..."
python3 /app/app.py &

# Start the main application that handles MQTT and API calls
echo "Starting MQTT service..."
python3 /app/run.py