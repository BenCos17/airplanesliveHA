import requests
import time
import json
import os
import paho.mqtt.client as mqtt

# Configuration
API_URL = "http://localhost:8000/api/airplanes"  # Local API
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 10))
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt://localhost")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "airplanes/live")

# MQTT Client Setup
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code: {rc}")

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER)

def fetch_data():
    while True:
        try:
            response = requests.get(API_URL)  # Fetch data from the local API
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
            print(f"Error fetching data from API: {e}")
        mqtt_client.loop_start()  # Start the MQTT loop
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    fetch_data()