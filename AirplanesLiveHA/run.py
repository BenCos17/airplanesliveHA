import os
import json
import time
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

def log(msg):
    print(f"[AirplanesLive] {msg}", flush=True)

# Load config from environment variables
API_URL = os.getenv("API_URL", "https://api.airplanes.live/v2/point")
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
        log(f"Fetching data from: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        log(f"Fetched {len(data) if isinstance(data, list) else 0} aircraft")
        return data
    except Exception as e:
        log(f"Error fetching airplane data: {e}")
        return None

def publish_discovery(client, hex_id, aircraft_data):
    """Publish MQTT discovery for Home Assistant"""
    discovery_topic = f"homeassistant/sensor/airplane_{hex_id}/config"
    
    # Extract useful information from aircraft data
    flight = aircraft_data.get('flight', 'Unknown')
    alt_baro = aircraft_data.get('alt_baro', 'Unknown')
    speed = aircraft_data.get('speed', 'Unknown')
    track = aircraft_data.get('track', 'Unknown')
    lat = aircraft_data.get('lat', 0)
    lon = aircraft_data.get('lon', 0)
    
    payload = {
        "name": f"Airplane {hex_id}",
        "state_topic": f"{MQTT_TOPIC}/{hex_id}/state",
        "json_attributes_topic": f"{MQTT_TOPIC}/{hex_id}/attributes",
        "unique_id": f"airplane_{hex_id}",
        "device_class": "sensor",
        "unit_of_measurement": "ft",
        "value_template": "{{ value_json.altitude }}",
        "device": {
            "identifiers": [f"airplane_{hex_id}"],
            "name": f"Airplane {hex_id}",
            "manufacturer": "airplanes.live",
            "model": aircraft_data.get('t', 'Unknown'),
            "sw_version": "1.0"
        }
    }
    
    try:
        client.publish(discovery_topic, json.dumps(payload), retain=True)
        log(f"Published discovery for {hex_id}")
    except Exception as e:
        log(f"Error publishing discovery for {hex_id}: {e}")

def publish_airplane_data(client, hex_id, aircraft_data):
    """Publish airplane data to MQTT"""
    try:
        # Publish state
        state_topic = f"{MQTT_TOPIC}/{hex_id}/state"
        state_payload = {
            "altitude": aircraft_data.get('alt_baro', 'Unknown'),
            "flight": aircraft_data.get('flight', 'Unknown'),
            "timestamp": datetime.now().isoformat()
        }
        client.publish(state_topic, json.dumps(state_payload), retain=True)
        
        # Publish attributes
        attr_topic = f"{MQTT_TOPIC}/{hex_id}/attributes"
        attr_payload = {
            "hex": hex_id,
            "flight": aircraft_data.get('flight', 'Unknown'),
            "altitude": aircraft_data.get('alt_baro', 'Unknown'),
            "speed": aircraft_data.get('speed', 'Unknown'),
            "track": aircraft_data.get('track', 'Unknown'),
            "latitude": aircraft_data.get('lat', 0),
            "longitude": aircraft_data.get('lon', 0),
            "type": aircraft_data.get('t', 'Unknown'),
            "registration": aircraft_data.get('r', 'Unknown'),
            "squawk": aircraft_data.get('squawk', 'Unknown'),
            "last_seen": datetime.now().isoformat()
        }
        client.publish(attr_topic, json.dumps(attr_payload), retain=True)
        
    except Exception as e:
        log(f"Error publishing data for {hex_id}: {e}")

def publish_airplanes(client, data):
    if not data or not isinstance(data, list):
        log("No valid aircraft data received")
        return
    
    log(f"Processing {len(data)} aircraft")
    for aircraft in data:
        hex_id = aircraft.get('hex')
        if hex_id:
            publish_discovery(client, hex_id, aircraft)
            publish_airplane_data(client, hex_id, aircraft)
        else:
            log("Aircraft data missing hex ID")

def on_connect(client, userdata, flags, reasonCode, properties):
    log(f"Connected to MQTT broker with reason code: {reasonCode}")

def on_disconnect(client, userdata, rc):
    log(f"Disconnected from MQTT broker with reason code: {rc}")

def main():
    log("Starting Airplanes Live Home Assistant Add-on")
    log(f"Configuration: API_URL={API_URL}, LAT={LATITUDE}, LON={LONGITUDE}, RADIUS={RADIUS}")
    log(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}")
    
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        log("MQTT authentication configured")
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Connect to MQTT broker with retry logic
    while True:
        try:
            log(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
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
            log(f"Sleeping for {UPDATE_INTERVAL} seconds")
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        log("Shutting down.")
    except Exception as e:
        log(f"Unexpected error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        log("Cleanup completed")

if __name__ == "__main__":
    main()