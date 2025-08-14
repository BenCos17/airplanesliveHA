import os
import json
import time
import logging
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def log(msg: str, level: str = "info"):
    """Log message with specified level"""
    if level == "debug":
        logger.debug(msg)
    elif level == "warning":
        logger.warning(msg)
    elif level == "error":
        logger.error(msg)
    elif level == "critical":
        logger.critical(msg)
    else:
        logger.info(msg)

def load_config():
    """Load configuration from Home Assistant options.json file"""
    config_path = "/data/options.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        log(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        log(f"Configuration file {config_path} not found, using defaults", "warning")
        return {}
    except json.JSONDecodeError as e:
        log(f"Error parsing configuration file: {e}, using defaults", "error")
        return {}
    except Exception as e:
        log(f"Error loading configuration: {e}, using defaults", "error")
        return {}

# Load configuration
config = load_config()

log(f"Raw config loaded: {config}")

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
TRACKING_MODE = config.get("tracking_mode", "summary")  # New: summary, detailed, both

log(f"Configuration loaded: API_URL={API_URL}, LAT={LATITUDE}, LON={LONGITUDE}, RADIUS={RADIUS}")
log(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}, Tracking Mode: {TRACKING_MODE}")

def validate_config():
    """Validate configuration values"""
    errors = []
    
    try:
        lat = float(LATITUDE)
        if not -90 <= lat <= 90:
            errors.append(f"Latitude {lat} is out of range (-90 to 90)")
    except ValueError:
        errors.append(f"Invalid latitude: {LATITUDE}")
    
    try:
        lon = float(LONGITUDE)
        if not -180 <= lon <= 180:
            errors.append(f"Longitude {lon} is out of range (-180 to 180)")
    except ValueError:
        errors.append(f"Invalid longitude: {LONGITUDE}")
    
    if not isinstance(RADIUS, (int, float)) or RADIUS <= 0:
        errors.append(f"Invalid radius: {RADIUS} (must be positive number)")
    
    if not isinstance(UPDATE_INTERVAL, (int, float)) or UPDATE_INTERVAL < 1:
        errors.append(f"Invalid update interval: {UPDATE_INTERVAL} (must be >= 1)")
    
    if errors:
        for error in errors:
            log(f"Configuration error: {error}", "error")
        return False
    
    log("Configuration validation passed")
    return True

def fetch_airplane_data() -> Optional[List[Dict[str, Any]]]:
    """Fetch airplane data from API with improved error handling"""
    url = f"{API_URL}/{LATITUDE}/{LONGITUDE}/{RADIUS}"
    
    try:
        log(f"Fetching data from: {url}")
        resp = requests.get(url, timeout=15)  # Increased timeout
        resp.raise_for_status()
        data = resp.json()
        
        # Extract aircraft array from response
        if isinstance(data, dict) and 'ac' in data:
            aircraft_list = data['ac']
            count = len(aircraft_list) if isinstance(aircraft_list, list) else 0
            log(f"Fetched {count} aircraft")
            return aircraft_list
        else:
            log(f"Unexpected API response format: {type(data)}", "warning")
            return None
            
    except requests.exceptions.Timeout:
        log("API request timed out", "error")
        return None
    except requests.exceptions.ConnectionError:
        log("Failed to connect to API - network error", "error")
        return None
    except requests.exceptions.HTTPError as e:
        log(f"API HTTP error: {e}", "error")
        return None
    except json.JSONDecodeError as e:
        log(f"Failed to parse API response: {e}", "error")
        return None
    except Exception as e:
        log(f"Unexpected error fetching airplane data: {e}", "error")
        return None

def publish_discovery(client):
    """Publish MQTT discovery for Home Assistant - single device with multiple sensors."""
    log("Starting MQTT discovery publishing...")
    
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
            "name": "Fastest Aircraft (Ground)",
            "key": "fastest_ground",
            "unit": "kts",
            "device_class": "speed",
            "value_template": "{{ value_json.fastest_ground }}"
        },
        {
            "name": "Fastest Aircraft (Air)",
            "key": "fastest_air",
            "unit": "kts",
            "device_class": "speed",
            "value_template": "{{ value_json.fastest_air }}"
        },
        {
            "name": "Aircraft Types",
            "key": "aircraft_types",
            "unit": None,
            "device_class": None,
            "value_template": "{{ value_json.aircraft_types }}"
        },
        {
            "name": "Weather Conditions",
            "key": "weather",
            "unit": None,
            "device_class": None,
            "value_template": "{{ value_json.weather }}"
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
            "name": sensor['name'],  # Remove the "Airplanes Live" prefix to avoid duplication
            "state_topic": f"{MQTT_TOPIC}/summary",
            "unique_id": f"airplanes_live_{sensor['key']}",
            "value_template": sensor["value_template"],
            "device": {
                "identifiers": ["airplanes_live_device"],
                "name": "Airplanes Live",
                "manufacturer": "BenCos17",
                "model": "Aircraft Tracker (Powered by airplanes.live)",
                "sw_version": "1.4.8"
            }
        }
        if sensor["unit"]:
            payload["unit_of_measurement"] = sensor["unit"]
        if sensor["device_class"]:
            payload["device_class"] = sensor["device_class"]

        try:
            payload_json = json.dumps(payload)
            log(f"Publishing discovery to {discovery_topic}: {payload_json}")
            client.publish(discovery_topic, payload_json, retain=True)
            log(f"Published discovery for {sensor['name']}")
        except Exception as e:
            log(f"Error publishing discovery for {sensor['name']}: {e}", "error")
    
    log("Discovery publishing completed")

def publish_individual_aircraft(client, aircraft_list):
    """Publish individual aircraft data if tracking mode allows it"""
    if TRACKING_MODE not in ["detailed", "both"]:
        return
    
    if not aircraft_list or not isinstance(aircraft_list, list):
        return
    
    log(f"Publishing individual aircraft data for {len(aircraft_list)} aircraft")
    
    for aircraft in aircraft_list:
        try:
            hex_code = aircraft.get('hex', 'unknown')
            if hex_code == 'unknown':
                continue
                
            # Publish aircraft state
            state_topic = f"{MQTT_TOPIC}/aircraft/{hex_code}/state"
            state_payload = {
                "hex": hex_code,
                "flight": aircraft.get('flight', 'Unknown'),
                "altitude": aircraft.get('alt_baro'),
                "speed": aircraft.get('gs') or aircraft.get('tas') or aircraft.get('ias'),  # Use correct speed fields
                "track": aircraft.get('track'),
                "lat": aircraft.get('lat'),
                "lon": aircraft.get('lon'),
                "last_seen": datetime.now().isoformat()
            }
            
            client.publish(state_topic, json.dumps(state_payload), retain=True)
            
            # Publish discovery for individual aircraft
            discovery_topic = f"homeassistant/sensor/airplane_{hex_code}_info/config"
            discovery_payload = {
                "name": f"Aircraft {hex_code}",
                "state_topic": state_topic,
                "unique_id": f"airplane_{hex_code}_info",
                "value_template": "{{ value_json.flight }}",
                "device": {
                    "identifiers": [f"airplane_{hex_code}"],
                    "name": f"Aircraft {hex_code}",
                    "manufacturer": "Unknown",
                    "model": aircraft.get('t', 'Unknown'),
                    "via_device": "airplanes_live_device"
                }
            }
            
            client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
            
        except Exception as e:
            log(f"Error publishing individual aircraft {hex_code}: {e}", "error")

def publish_summary_data(client, aircraft_list):
    """Publish summary data to MQTT with improved error handling"""
    try:
        if not aircraft_list or not isinstance(aircraft_list, list):
            # No aircraft data
            summary_payload = {
                "count": 0,
                "closest": "None",
                "highest": 0,
                "fastest_ground": 0,
                "fastest_air": 0,
                "last_update": datetime.now().isoformat()
            }
        else:
            # Process aircraft data
            count = len(aircraft_list)
            log(f"Processing {count} aircraft for summary data")
            
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
                
                log(f"Found {len(valid_aircraft)} aircraft with valid altitude data")
                
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
                
                log(f"Found {len(altitudes)} valid altitude values")
                if altitudes:
                    highest = max(altitudes)
                    log(f"Highest altitude: {highest}ft")
                else:
                    log("No valid altitude data found")
            
            # Find fastest aircraft (ground speed)
            fastest_ground = 0
            if aircraft_list:
                ground_speeds = []
                for ac in aircraft_list:
                    speed = ac.get('gs')  # Ground speed
                    if speed is not None:
                        try:
                            speed_num = float(speed)
                            ground_speeds.append(speed_num)
                        except (ValueError, TypeError):
                            continue
                
                log(f"Found {len(ground_speeds)} valid ground speed values")
                if ground_speeds:
                    fastest_ground = max(ground_speeds)
                    log(f"Fastest ground speed: {fastest_ground}kts")
                else:
                    log("No valid ground speed data found")
            
            # Find fastest aircraft (air speed)
            fastest_air = 0
            if aircraft_list:
                air_speeds = []
                for ac in aircraft_list:
                    # Try airspeed fields
                    speed = ac.get('tas')  # True airspeed
                    if speed is None:
                        speed = ac.get('ias')  # Indicated airspeed
                    
                    if speed is not None:
                        try:
                            speed_num = float(speed)
                            air_speeds.append(speed_num)
                        except (ValueError, TypeError):
                            continue
                
                log(f"Found {len(air_speeds)} valid air speed values")
                if air_speeds:
                    fastest_air = max(air_speeds)
                    log(f"Fastest air speed: {fastest_air}kts")
                else:
                    log("No valid air speed data found")
            
            # Collect aircraft types
            aircraft_types = []
            if aircraft_list:
                for ac in aircraft_list:
                    ac_type = ac.get('t')  # Aircraft type code
                    ac_desc = ac.get('desc')  # Full description
                    if ac_type and ac_type not in aircraft_types:
                        aircraft_types.append(ac_type)
            
            # Collect weather conditions
            weather_info = "Unknown"
            if aircraft_list:
                # Get weather data from first aircraft with valid data
                for ac in aircraft_list:
                    wind_dir = ac.get('wd')
                    wind_speed = ac.get('ws')
                    temp = ac.get('oat')
                    if wind_dir is not None or wind_speed is not None or temp is not None:
                        weather_parts = []
                        if wind_dir is not None:
                            weather_parts.append(f"Wind: {wind_dir}°")
                        if wind_speed is not None:
                            weather_parts.append(f"{wind_speed}kts")
                        if temp is not None:
                            weather_parts.append(f"Temp: {temp}°C")
                        weather_info = " | ".join(weather_parts)
                        break
            
            summary_payload = {
                "count": count,
                "closest": closest,
                "highest": highest,
                "fastest_ground": fastest_ground,
                "fastest_air": fastest_air,
                "aircraft_types": ", ".join(aircraft_types) if aircraft_types else "Unknown",
                "weather": weather_info,
                "last_update": datetime.now().isoformat()
            }
        
        # Publish summary data
        summary_topic = f"{MQTT_TOPIC}/summary"
        client.publish(summary_topic, json.dumps(summary_payload), retain=True)
        
        log(f"Published summary: {count} aircraft, closest: {summary_payload['closest']}, highest: {highest}ft, fastest ground: {fastest_ground}kts, fastest air: {fastest_air}kts, types: {summary_payload['aircraft_types']}, weather: {summary_payload['weather']}")
        
    except Exception as e:
        log(f"Error publishing summary data: {e}", "error")
        # Log the aircraft data for debugging
        if aircraft_list:
            log(f"Aircraft data sample: {aircraft_list[:2]}", "error")

def on_connect(client, userdata, flags, reasonCode, properties):
    if reasonCode == 0:
        log("Connected to MQTT broker successfully")
    else:
        log(f"Connected to MQTT broker with reason code: {reasonCode}", "warning")
        if reasonCode == 5:
            log("MQTT authentication failed - check username/password", "error")

def on_disconnect(client, userdata, rc, properties=None):
    log(f"Disconnected from MQTT broker with reason code: {rc}", "warning")

def main():
    log("Starting Airplanes Live Home Assistant Add-on v1.4.0")
    
    # Validate configuration first
    if not validate_config():
        log("Configuration validation failed. Please check your settings.", "critical")
        return
    
    log(f"Configuration: API_URL={API_URL}, LAT={LATITUDE}, LON={LONGITUDE}, RADIUS={RADIUS}")
    log(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}")
    
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    
    # Configure MQTT authentication if credentials are provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        log("MQTT authentication configured")
    else:
        log("No MQTT credentials provided - attempting anonymous connection", "warning")
    
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
                log("MQTT connection failed - retrying...", "warning")
                client.loop_stop()
                retry_count += 1
                time.sleep(5)
                
        except Exception as e:
            log(f"MQTT connection failed: {e}. Retrying in 5 seconds...", "error")
            retry_count += 1
            time.sleep(5)
    
    if not client.is_connected():
        log("Failed to connect to MQTT broker after maximum retries. Continuing without MQTT...", "critical")
        client = None

    try:
        # Publish discovery once at startup
        if client and client.is_connected():
            publish_discovery(client)
            # Wait a moment for discovery to be processed
            time.sleep(3)
            # Publish initial data to help with discovery
            log("Publishing initial data for discovery...")
            initial_data = {
                "count": 0,
                "closest": "None",
                "highest": 0,
                "fastest_ground": 0,
                "fastest_air": 0,
                "aircraft_types": "None",
                "weather": "Unknown",
                "last_update": datetime.now().isoformat()
            }
            client.publish(f"{MQTT_TOPIC}/summary", json.dumps(initial_data), retain=True)
            log("Initial data published")
        
        while True:
            data = fetch_airplane_data()
            if client and client.is_connected():
                publish_summary_data(client, data)
                publish_individual_aircraft(client, data)
            else:
                log("MQTT not connected - skipping publish", "warning")
            log(f"Sleeping for {UPDATE_INTERVAL} seconds")
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        log("Shutting down.")
    except Exception as e:
        log(f"Unexpected error: {e}", "critical")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        log("Cleanup completed")

if __name__ == "__main__":
    main()