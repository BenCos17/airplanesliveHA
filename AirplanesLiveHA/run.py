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

def publish_discovery(client):
    """Publish MQTT discovery for Home Assistant - single device with multiple sensors."""
    # Define the sensors we want to expose
    sensors = [
        {
            "name": "Aircraft Count",
            "key": "count",
            "unit": None,
            "device_class": None,
            "value_template": "{{ value_json.count }}"
        },
        {
            "name": "Closest Aircraft",
            "key": "closest",
            "unit": None,
            "device_class": None,
            "value_template": "{{ value_json.closest }}"
        },
        {
            "name": "Highest Aircraft",
            "key": "highest",
            "unit": "ft",
            "device_class": None,
            "value_template": "{{ value_json.highest }}"
        },
        {
            "name": "Fastest Aircraft",
            "key": "fastest",
            "unit": "kts",
            "device_class": "speed",
            "value_template": "{{ value_json.fastest }}"
        },
        {
            "name": "Last Update",
            "key": "last_update",
            "unit": None,
            "device_class": "timestamp",
            "value_template": "{{ value_json.last_update }}"
        }
    ]

    for sensor in sensors:
        discovery_topic = f"homeassistant/sensor/airplanes_live_{sensor['key']}/config"
        payload = {
            "name": f"Airplanes Live {sensor['name']}",
            "state_topic": f"{MQTT_TOPIC}/summary",
            "unique_id": f"airplanes_live_{sensor['key']}",
            "value_template": sensor["value_template"],
            "device": {
                "identifiers": ["airplanes_live_device"],
                "name": "Airplanes Live",
                "manufacturer": "airplanes.live",
                "model": "Aircraft Tracker",
                "sw_version": "1.0"
            }
        }
        if sensor["unit"]:
            payload["unit_of_measurement"] = sensor["unit"]
        if sensor["device_class"]:
            payload["device_class"] = sensor["device_class"]

        try:
            client.publish(discovery_topic, json.dumps(payload), retain=True)
            log(f"Published discovery for {sensor['name']}")
        except Exception as e:
            log(f"Error publishing discovery for {sensor['name']}: {e}")

def publish_summary_data(client, aircraft_list):
    """Publish summary data to MQTT"""
    try:
        if not aircraft_list or not isinstance(aircraft_list, list):
            # No aircraft data
            summary_payload = {
                "count": 0,
                "closest": "None",
                "highest": 0,
                "fastest": 0,
                "last_update": datetime.now().isoformat()
            }
        else:
            # Process aircraft data
            count = len(aircraft_list)
            
            # Find closest aircraft (lowest altitude, or first one if no altitude data)
            closest = "None"
            if aircraft_list:
                # Filter aircraft with valid altitude data and convert to numbers
                valid_aircraft = []
                for ac in aircraft_list:
                    alt = ac.get('alt_baro')
                    if alt is not None:
                        try:
                            alt_num = float(alt)
                            valid_aircraft.append((ac, alt_num))
                        except (ValueError, TypeError):
                            continue
                
                if valid_aircraft:
                    # Find aircraft with lowest altitude
                    closest_aircraft, closest_alt = min(valid_aircraft, key=lambda x: x[1])
                    flight = closest_aircraft.get('flight', 'Unknown')
                    closest = f"{flight} ({closest_alt}ft)"
                else:
                    # No valid altitude data, use first aircraft
                    closest_aircraft = aircraft_list[0]
                    closest = closest_aircraft.get('flight', 'Unknown')
            
            # Find highest aircraft
            highest = 0
            if aircraft_list:
                altitudes = []
                for ac in aircraft_list:
                    alt = ac.get('alt_baro')
                    if alt is not None:
                        try:
                            alt_num = float(alt)
                            altitudes.append(alt_num)
                        except (ValueError, TypeError):
                            continue
                if altitudes:
                    highest = max(altitudes)
            
            # Find fastest aircraft
            fastest = 0
            if aircraft_list:
                speeds = []
                for ac in aircraft_list:
                    speed = ac.get('speed')
                    if speed is not None:
                        try:
                            speed_num = float(speed)
                            speeds.append(speed_num)
                        except (ValueError, TypeError):
                            continue
                if speeds:
                    fastest = max(speeds)
            
            summary_payload = {
                "count": count,
                "closest": closest,
                "highest": highest,
                "fastest": fastest,
                "last_update": datetime.now().isoformat()
            }
        
        # Publish summary data
        summary_topic = f"{MQTT_TOPIC}/summary"
        client.publish(summary_topic, json.dumps(summary_payload), retain=True)
        
        log(f"Published summary: {count} aircraft, closest: {summary_payload['closest']}, highest: {highest}ft, fastest: {fastest}kts")
        
    except Exception as e:
        log(f"Error publishing summary data: {e}")

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
        # Publish discovery once at startup
        if client and client.is_connected():
            publish_discovery(client)
        
        while True:
            data = fetch_airplane_data()
            if client and client.is_connected():
                publish_summary_data(client, data)
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