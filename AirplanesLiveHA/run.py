import requests
import time
import json
import os
import paho.mqtt.client as mqtt

# Configuration
API_URLS = [
    "https://api.airplanes.live/v2/mil",  # Military aircraft
    "https://api.airplanes.live/v2/ladd",  # LADD aircraft
    "https://api.airplanes.live/v2/pia",   # PIA aircraft
    "https://api.airplanes.live/v2/hex/[hex]",  # Replace [hex] with actual hex ID
    "https://api.airplanes.live/v2/callsign/[callsign]",  # Replace [callsign] with actual callsign
    "https://api.airplanes.live/v2/reg/[reg]",  # Replace [reg] with actual registration
    "https://api.airplanes.live/v2/type/[type]",  # Replace [type] with actual ICAO type code
    "https://api.airplanes.live/v2/squawk/[squawk]",  # Replace [squawk] with actual squawk code
    "https://api.airplanes.live/v2/point/[lat]/[lon]/[radius]"  # Replace [lat], [lon], and [radius] with actual values
]  # List of endpoints to poll
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 10))
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt://localhost")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "airplanes/live")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

# MQTT Client Setup
mqtt_client = mqtt.Client()

# Set username and password if provided
if MQTT_USERNAME and MQTT_PASSWORD:
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code: {rc}")

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER)

def fetch_data():
    while True:
        for api_url in API_URLS:  # Iterate over each API URL
            try:
                # Note: You need to replace placeholders with actual values before making the request
                response = requests.get(api_url)  # Fetch data from the current API
                response.raise_for_status()
                data = response.json()

                # Process and publish data for the map
                for airplane in data.get('recentReceiverIds', []):
                    hex_id = airplane.get('hex')
                    flight = airplane.get('flight', 'Unknown Flight')
                    state = airplane.get('alt_hgt', 'Unknown Altitude')

                    # Assuming the API provides latitude and longitude
                    latitude = airplane.get('lat', None)
                    longitude = airplane.get('lon', None)

                    attributes = {
                        "flight": flight,
                        "altitude": airplane.get('altitude', 'N/A'),
                        "heading": airplane.get('nav_heading', 'N/A'),
                        "airline": airplane.get('airline', 'Unknown'),
                        "latitude": latitude,
                        "longitude": longitude,
                    }

                    # Publish data to MQTT for the map
                    mqtt_client.publish(f"{MQTT_TOPIC}/{hex_id}", json.dumps({
                        "state": state,
                        "attributes": attributes
                    }))

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from API {api_url}: {e}")
        mqtt_client.loop_start()  # Start the MQTT loop
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    fetch_data()