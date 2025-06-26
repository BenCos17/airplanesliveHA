import os
import json
import time
import requests
import paho.mqtt.client as mqtt

def log(msg):
    print(f"[AirplanesLive] {msg}", flush=True)

# Load config from environment variables
API_URL = os.getenv("API_URL", "https://airplanes.live/api/point")
LATITUDE = os.getenv("LATITUDE", "53.2707")
LONGITUDE = os.getenv("LONGITUDE", "-9.0568")
RADIUS = os.getenv("RADIUS", "50")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 10))
MQTT_BROKER = os.getenv("MQTT_BROKER", "core-mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "airplanes/live")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

def fetch_airplane_data():
    url = f"{API_URL}/{LATITUDE}/{LONGITUDE}/{RADIUS}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log(f"Error fetching airplane data: {e}")
        return None

def publish_discovery(client, hex_id):
    discovery_topic = f"homeassistant/sensor/airplane_{hex_id}/config"
    payload = {
        "name": f"Airplane {hex_id}",
        "state_topic": f"{MQTT_TOPIC}/{hex_id}",
        "json_attributes_topic": f"{MQTT_TOPIC}/{hex_id}",
        "unique_id": f"airplane_{hex_id}",
        "device": {
            "identifiers": [f"airplane_{hex_id}"],
            "name": f"Airplane {hex_id}",
            "manufacturer": "airplanes.live"
        }
    }
    client.publish(discovery_topic, json.dumps(payload), retain=True)

def publish_airplanes(client, data):
    if not data:
        return
    for aircraft in data:
        hex_id = aircraft.get('hex', 'unknown')
        publish_discovery(client, hex_id)
        topic = f"{MQTT_TOPIC}/{hex_id}"
        client.publish(topic, json.dumps(aircraft), retain=True)

def on_connect(client, userdata, flags, reasonCode, properties):
    log("Connected to MQTT broker2")

def main():
    log("Starting Airplanes Live Home Assistant Add-on")
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect

    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            break
        except Exception as e:
            log(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    try:
        while True:
            data = fetch_airplane_data()
            publish_airplanes(client, data)
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        log("Shutting down.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()