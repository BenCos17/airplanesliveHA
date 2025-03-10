import os
import json
import time
import requests
import paho.mqtt.client as mqtt

# Load config from environment variables
API_URL = os.getenv("API_URL", "https://airplanes.live/api/point")
LATITUDE = os.getenv("LATITUDE", "53.2707")
LONGITUDE = os.getenv("LONGITUDE", "-9.0568")
RADIUS = os.getenv("RADIUS", "50")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 10))
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt://localhost").replace("mqtt://", "")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "airplanes/live")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

# Initialize MQTT client
client = mqtt.Client()
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

client.connect(MQTT_BROKER, 1883, 60)

def fetch_airplane_data():
    """Fetches live airplane data from the Airplanes.Live API."""
    url = f"{API_URL}/{LATITUDE}/{LONGITUDE}/{RADIUS}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def publish_to_mqtt(data):
    """Publishes airplane data to the configured MQTT topic."""
    if data:
        for aircraft in data:
            message = json.dumps(aircraft)
            topic = f"{MQTT_TOPIC}/{aircraft.get
