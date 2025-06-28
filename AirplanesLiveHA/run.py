import os
import json
import time
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

def log(msg):
    print(f"[AirplanesLive] {msg}", flush=True)

def load_config():
    """Load configuration from Home Assistant options.json file"""
    config_path = "/data/options.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        log(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        log(f"Configuration file {config_path} not found, using defaults")
        return {}
    except json.JSONDecodeError as e:
        log(f"Error parsing configuration file: {e}, using defaults")
        return {}
    except Exception as e:
        log(f"Error loading configuration: {e}, using defaults")
        return {}

# Load configuration
config = load_config()

print(f"[AirplanesLive] Raw config loaded: {config}")

# Load config from options.json with fallback defaults
API_URL = config.get("api_url", "https://api.airplanes.live/v2/point")
LATITUDE = config.get("latitude", "53.2707")
LONGITUDE = config.get("longitude", "-9.0568")
RADIUS = config.get("radius", 50)
UPDATE_INTERVAL = config.get("update_interval", 10)
MQTT_BROKER = config.get("mqtt_broker", "core-mosquitto")
MQTT_PORT = config.get("mqtt_port", 1883)
MQTT_TOPIC = config.get("mqtt_topic", "airplanes/live")
MQTT_USERNAME = config.get("mqtt_username", "")
MQTT_PASSWORD = config.get("mqtt_password", "")

log(f"Configuration loaded: API_URL={API_URL}, LAT={LATITUDE}, LON={LONGITUDE}, RADIUS={RADIUS}")
log(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}")

def fetch_airplane_data():
    url = f"{API_URL}/{LATITUDE}/{LONGITUDE}/{RADIUS}"
    try:
        log(f"Fetching data from: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract aircraft array from response
        if isinstance(data, dict) and 'ac' in data:
            aircraft_list = data['ac']
            log(f"Fetched {len(aircraft_list) if isinstance(aircraft_list, list) else 0} aircraft")
            return aircraft_list
        else:
            log(f"Unexpected API response format: {type(data)}")
            return None
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
    if reasonCode == 0:
        log(f"Connected to MQTT broker successfully")
    else:
        log(f"Connected to MQTT broker with reason code: {reasonCode}")
        if reasonCode == 5:
            log("MQTT authentication failed - check username/password")

def on_disconnect(client, userdata, rc, properties=None):
    log(f"Disconnected from MQTT broker with reason code: {rc}")

def main():
    log("Starting Airplanes Live Home Assistant Add-on")
    log(f"Configuration: API_URL={API_URL}, LAT={LATITUDE}, LON={LONGITUDE}, RADIUS={RADIUS}")
    log(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}")
    
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    
    # Configure MQTT authentication if credentials are provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        log("MQTT authentication configured")
    else:
        log("No MQTT credentials provided - attempting anonymous connection")
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Connect to MQTT broker with retry logic
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            log(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} (attempt {retry_count + 1}/{max_retries})")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            
            # Wait a moment to see if connection is successful
            time.sleep(2)
            if client.is_connected():
                log("MQTT connection established successfully")
                break
            else:
                log("MQTT connection failed - retrying...")
                client.loop_stop()
                retry_count += 1
                time.sleep(5)
                
        except Exception as e:
            log(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
            retry_count += 1
            time.sleep(5)
    
    if not client.is_connected():
        log("Failed to connect to MQTT broker after maximum retries. Continuing without MQTT...")
        client = None

    try:
        while True:
            data = fetch_airplane_data()
            if client and client.is_connected():
                publish_airplanes(client, data)
            else:
                log("MQTT not connected - skipping publish")
            log(f"Sleeping for {UPDATE_INTERVAL} seconds")
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        log("Shutting down.")
    except Exception as e:
        log(f"Unexpected error: {e}")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        log("Cleanup completed")

if __name__ == "__main__":
    main()