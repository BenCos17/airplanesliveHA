import os
import json
import time
import logging
import requests
import paho.mqtt.client as mqtt
import math
from datetime import datetime
from typing import Optional, List, Dict, Any
import yaml
from queue import Queue
import threading

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

def get_addon_version():
    """Get addon version from config.yaml file"""
    config_path = "config.yaml"
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        version = config.get('version', 'unknown')
        log(f"Loaded addon version: {version}")
        return version
    except FileNotFoundError:
        log(f"Config file {config_path} not found, using default version", "warning")
        return "1.4.29"
    except yaml.YAMLError as e:
        log(f"Error parsing config.yaml: {e}, using default version", "error")
        return "1.4.29"
    except Exception as e:
        log(f"Error loading version: {e}, using default version", "error")
        return "1.4.29"

# Load configuration
config = load_config()

log(f"Raw config loaded: {config}")

# Load config from options.json with fallback defaults
API_TYPE = config.get("api_type", "unauthenticated")
API_KEY = config.get("api_key", "")
DISABLE_AUTO_CONFIG = config.get("disable_auto_config", False)
LATITUDE = config.get("latitude", "53.2707")
LONGITUDE = config.get("longitude", "-9.0568")
RADIUS = config.get("radius", 50)
UPDATE_INTERVAL = config.get("update_interval", 10)
MQTT_BROKER = config.get("mqtt_broker", "core-mosquitto")
MQTT_PORT = config.get("mqtt_port", 1883)
MQTT_TOPIC = config.get("mqtt_topic", "airplanes/live")
MQTT_USERNAME = config.get("mqtt_username", "")
MQTT_PASSWORD = config.get("mqtt_password", "")
MQTT_QOS = config.get("mqtt_qos", 1)  # Default to QoS 1 for reliability
MQTT_RETAIN = config.get("mqtt_retain", True)  # Default to retain messages
TRACKING_MODE = config.get("tracking_mode", "summary")

# Auto-configure API URL based on type (unless disabled)
if DISABLE_AUTO_CONFIG:
    # Use user-provided URL and radius as-is
    API_URL = config.get("api_url", "https://api.airplanes.live/v2/point")
    RADIUS_NMI = RADIUS
    log("Auto-configuration disabled - using user-provided settings")
else:
    # Auto-configure based on API type
    if API_TYPE == "authenticated":
        API_URL = "https://rest.api.airplanes.live"
        # Convert radius from km to nautical miles for REST API
        RADIUS_NMI = RADIUS * 0.539957
        log("Auto-configured for REST API with radius conversion")
    else:
        # Feeder API uses kilometers
        API_URL = "https://api.airplanes.live/v2/point"
        RADIUS_NMI = RADIUS
        log("Auto-configured for feeder API")

log(f"Configuration loaded: API_TYPE={API_TYPE}, API_URL={API_URL}, LAT={LATITUDE}, LON={LONGITUDE}, RADIUS={RADIUS}km ({RADIUS_NMI:.1f}nm)")
log(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}, QoS: {MQTT_QOS}, Retain: {MQTT_RETAIN}, Tracking Mode: {TRACKING_MODE}")

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
    
    # Validate MQTT QoS
    if not isinstance(MQTT_QOS, int) or MQTT_QOS not in [0, 1, 2]:
        errors.append(f"Invalid MQTT QoS: {MQTT_QOS} (must be 0, 1, or 2)")
    
    # Validate MQTT retain
    if not isinstance(MQTT_RETAIN, bool):
        errors.append(f"Invalid MQTT retain: {MQTT_RETAIN} (must be boolean)")
    
    if errors:
        for error in errors:
            log(f"Configuration error: {error}", "error")
        return False
    
    log("Configuration validation passed")
    return True

def fetch_airplane_data() -> Optional[List[Dict[str, Any]]]:
    """Fetch airplane data from API with improved error handling"""
    
    # Construct URL based on API type
    if API_TYPE == "authenticated":
        # REST API with circle query and filters
        url = f"{API_URL}/?circle={LATITUDE},{LONGITUDE},{RADIUS_NMI:.1f}"
        headers = {}
        if API_KEY:
            headers["auth"] = API_KEY
    else:
        # Feeder API
        url = f"{API_URL}/{LATITUDE}/{LONGITUDE}/{RADIUS}"
        headers = {}
    
    try:
        log(f"Fetching data from: {url}")
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        # Debug: Log response structure
        log(f"API response type: {type(data)}")
        if isinstance(data, dict):
            log(f"API response keys: {list(data.keys())}")
            if 'aircraft' in data:
                log(f"API response 'aircraft' type: {type(data['aircraft'])}")
            elif 'ac' in data:
                log(f"API response 'ac' type: {type(data['ac'])}")
        
        # Extract aircraft array from response
        if isinstance(data, dict):
            if 'aircraft' in data:
                aircraft_list = data['aircraft']
                if isinstance(aircraft_list, list):
                    count = len(aircraft_list)
                    log(f"Fetched {count} aircraft using {API_TYPE} API")
                    return aircraft_list
                else:
                    log(f"API response 'aircraft' field is not a list: {type(aircraft_list)}", "warning")
                    return None
            elif 'ac' in data:
                # Fallback for older API format
                aircraft_list = data['ac']
                if isinstance(aircraft_list, list):
                    count = len(aircraft_list)
                    log(f"Fetched {count} aircraft using {API_TYPE} API (legacy format)")
                    return aircraft_list
                else:
                    log(f"API response 'ac' field is not a list: {type(aircraft_list)}", "warning")
                    return None
            else:
                log(f"API response missing 'aircraft' or 'ac' field. Available keys: {list(data.keys())}", "warning")
                return None
        else:
            log(f"API response is not a dictionary: {type(data)}", "warning")
            return None
            
    except requests.exceptions.Timeout:
        log("API request timed out", "error")
        return None
    except requests.exceptions.ConnectionError:
        log("Failed to connect to API - network error", "error")
        return None
    except requests.exceptions.HTTPError as e:
        log(f"API HTTP error: {e}", "error")
        if "403" in str(e):
            log("403 Forbidden - Check your API key or switch to feeder API", "error")
        return None
    except json.JSONDecodeError as e:
        log(f"Failed to parse API response: {e}", "error")
        return None
    except Exception as e:
        log(f"Unexpected error fetching airplane data: {e}", "error")
        return None

def publish_discovery(mqtt_manager):
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
            "name": "Lowest Altitude Aircraft",
            "key": "closest_lowest",
            "unit": None,
            "device_class": None,
            "value_template": "{{ value_json.closest_lowest }}"
        },
        {
            "name": "Closest Distance Aircraft",
            "key": "closest_distance",
            "unit": None,
            "device_class": None,
            "value_template": "{{ value_json.closest_distance }}"
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
            "device_class": None,
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
                "sw_version": get_addon_version()
            }
        }
        if sensor["unit"]:
            payload["unit_of_measurement"] = sensor["unit"]
        if sensor["device_class"]:
            payload["device_class"] = sensor["device_class"]

        try:
            payload_json = json.dumps(payload)
            log(f"Publishing discovery to {discovery_topic}: {payload_json}")
            mqtt_manager.publish(discovery_topic, payload_json, retain=True)
            log(f"Published discovery for {sensor['name']}")
        except Exception as e:
            log(f"Error publishing discovery for {sensor['name']}: {e}", "error")
    
    log("Discovery publishing completed")

def publish_individual_aircraft(mqtt_manager, aircraft_list):
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
            
            mqtt_manager.publish(state_topic, json.dumps(state_payload), retain=True)
            
            # Publish discovery for individual aircraft
            discovery_topic = f"homeassistant/sensor/airplane_{hex_code}_info/config"
            discovery_payload = {
                "name": f"Aircraft {hex_code}",
                "value_template": "{{ value_json.flight }}",
                "device": {
                    "identifiers": [f"airplane_{hex_code}"],
                    "name": f"Aircraft {hex_code}",
                    "manufacturer": "Unknown",
                    "model": aircraft.get('t', 'Unknown'),
                    "via_device": "airplanes_live_device"
                }
            }
            
            mqtt_manager.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
            
        except Exception as e:
            log(f"Error publishing individual aircraft {hex_code}: {e}", "error")

def publish_summary_data(mqtt_manager, aircraft_list):
    """Publish summary data to MQTT with improved error handling"""
    try:
        if not aircraft_list or not isinstance(aircraft_list, list):
            # No aircraft data
            summary_payload = {
                "count": 0,
                "closest_lowest": "None",
                "closest_distance": "None",
                "highest": "None",
                "fastest_ground": 0,
                "fastest_air": 0,
                "aircraft_types": "None",
                "weather": "Unknown",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            # Process aircraft data
            count = len(aircraft_list)
            log(f"Processing {count} aircraft for summary data")
            
            # Find closest aircraft (lowest altitude)
            closest_lowest = "None"
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
                    closest_lowest = f"{flight} ({closest_alt}ft)"
                else:
                    # No valid altitude data, use first aircraft
                    closest_aircraft = aircraft_list[0]
                    closest_lowest = closest_aircraft.get('flight', 'Unknown')
            
            # Find geographically closest aircraft
            closest_distance = "None"
            if aircraft_list:
                # Calculate distance for each aircraft from your location
                aircraft_distances = []
                for ac in aircraft_list:
                    lat = ac.get('lat')
                    lon = ac.get('lon')
                    if lat is not None and lon is not None:
                        try:
                            # Calculate distance using Haversine formula
                            lat1, lon1 = float(LATITUDE), float(LONGITUDE)
                            lat2, lon2 = float(lat), float(lon)
                            
                            # Convert to radians
                            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
                            
                            # Haversine formula
                            dlat = lat2 - lat1
                            dlon = lon2 - lon1
                            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                            c = 2 * math.asin(math.sqrt(a))
                            distance_km = 6371 * c  # Earth's radius in km
                            
                            aircraft_distances.append((ac, distance_km))
                        except (ValueError, TypeError):
                            continue
                
                log(f"Found {len(aircraft_distances)} aircraft with valid position data")
                
                if aircraft_distances:
                    # Find aircraft with shortest distance
                    closest_aircraft, closest_dist = min(aircraft_distances, key=lambda x: x[1])
                    flight = closest_aircraft.get('flight', 'Unknown')
                    closest_distance = f"{flight} ({closest_dist:.1f}km)"
                else:
                    # No valid position data
                    closest_distance = "Unknown"
            
            # Find highest aircraft
            highest = 0
            highest_aircraft = None
            if aircraft_list:
                altitudes = []
                for ac in aircraft_list:
                    alt = ac.get('alt_baro')
                    if alt is not None:
                        try:
                            alt_num = float(alt)
                            altitudes.append((ac, alt_num))
                        except (ValueError, TypeError):
                            continue
                
                log(f"Found {len(altitudes)} valid altitude values")
                if altitudes:
                    # Find aircraft with highest altitude
                    highest_aircraft, highest = max(altitudes, key=lambda x: x[1])
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
                "closest_lowest": closest_lowest,
                "closest_distance": closest_distance,
                "highest": f"{highest_aircraft.get('flight', 'Unknown')} ({highest}ft)" if highest_aircraft else highest,
                "fastest_ground": fastest_ground,
                "fastest_air": fastest_air,
                "aircraft_types": ", ".join(aircraft_types) if aircraft_types else "Unknown",
                "weather": weather_info,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Debug: Log the summary payload structure
        log(f"Summary payload keys: {list(summary_payload.keys())}")
        
        # Publish summary data
        summary_topic = f"{MQTT_TOPIC}/summary"
        mqtt_manager.publish(summary_topic, json.dumps(summary_payload), retain=True)
        
        log(f"Published summary: {summary_payload.get('count', 'N/A')} aircraft, lowest: {summary_payload.get('closest_lowest', 'N/A')}, closest: {summary_payload.get('closest_distance', 'N/A')}, highest: {summary_payload.get('highest', 'N/A')}ft, fastest ground: {summary_payload.get('fastest_ground', 'N/A')}kts, fastest air: {summary_payload.get('fastest_air', 'N/A')}kts, types: {summary_payload.get('aircraft_types', 'N/A')}, weather: {summary_payload.get('weather', 'N/A')}")
        
    except Exception as e:
        log(f"Error publishing summary data: {e}", "error")
        # Log the aircraft data for debugging
        if aircraft_list:
            log(f"Aircraft data sample: {aircraft_list[:2]}", "error")

# MQTT Configuration and State
class MQTTManager:
    def __init__(self, broker: str, port: int, topic: str, username: str = "", password: str = ""):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        self.reconnect_delay = 1
        self.max_reconnect_delay = 300  # 5 minutes
        self.message_queue = Queue()
        self.last_heartbeat = 0
        self.heartbeat_interval = 30  # seconds
        self.connection_lock = threading.Lock()
        self.qos = 1
        self.retain = True
        
    def create_client(self):
        """Create and configure MQTT client"""
        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_log = self._on_log
        
        # Configure authentication
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
            log("MQTT authentication configured")
        else:
            log("No MQTT credentials provided - attempting anonymous connection", "warning")
        
        # Set last will and testament
        will_topic = f"{self.topic}/status"
        will_payload = json.dumps({
            "status": "offline",
            "last_seen": datetime.now().isoformat(),
            "reason": "unexpected_disconnect"
        })
        self.client.will_set(will_topic, will_payload, qos=1, retain=True)
        
        # Set connection parameters
        self.client.reconnect_delay_set(min_delay=1, max_delay=300)
        
        return self.client
    
    def _on_connect(self, client, userdata, flags, reasonCode, properties):
        """Handle MQTT connection events"""
        if reasonCode == 0:
            self.connected = True
            self.reconnect_delay = 1  # Reset delay on successful connection
            log("Connected to MQTT broker successfully")
            
            # Publish online status
            self._publish_status("online", "startup")
            
            # Process queued messages
            self._process_message_queue()
            
        else:
            self.connected = False
            log(f"Connected to MQTT broker with reason code: {reasonCode}", "warning")
            if reasonCode == 5:
                log("MQTT authentication failed - check username/password", "error")
            elif reasonCode == 3:
                log("MQTT broker unavailable - check if broker is running", "error")
            elif reasonCode == 4:
                log("MQTT bad username or password", "error")
    
    def _on_disconnect(self, client, userdata, rc, properties=None):
        """Handle MQTT disconnection events"""
        self.connected = False
        log(f"Disconnected from MQTT broker with reason code: {rc}", "warning")
        
        if rc == 0:
            log("Clean disconnect - shutting down")
        elif rc == 1:
            log("Unexpected disconnect - will attempt reconnection")
        elif rc == 2:
            log("Disconnect due to protocol error")
        elif rc == 3:
            log("Disconnect due to broker error")
        elif rc == 4:
            log("Disconnect due to authentication error")
        elif rc == 5:
            log("Disconnect due to authorization error")
        else:
            log(f"Disconnect with unknown reason code: {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """Handle successful message publish"""
        log(f"Message published successfully (ID: {mid})", "debug")
    
    def _on_log(self, client, userdata, level, buf):
        """Handle MQTT client logs"""
        if level == mqtt.MQTT_LOG_ERR:
            log(f"MQTT Error: {buf}", "error")
        elif level == mqtt.MQTT_LOG_WARNING:
            log(f"MQTT Warning: {buf}", "warning")
        elif level == mqtt.MQTT_LOG_INFO:
            log(f"MQTT Info: {buf}", "info")
        else:
            log(f"MQTT Debug: {buf}", "debug")
    
    def _publish_status(self, status: str, reason: str):
        """Publish connection status"""
        if not self.connected:
            return
            
        status_topic = f"{self.topic}/status"
        status_payload = json.dumps({
            "status": status,
            "last_seen": datetime.now().isoformat(),
            "reason": reason,
            "broker": f"{self.broker}:{self.port}"
        })
        
        try:
            self.client.publish(status_topic, status_payload, qos=1, retain=True)
            log(f"Published status: {status} ({reason})")
        except Exception as e:
            log(f"Error publishing status: {e}", "error")
    
    def _process_message_queue(self):
        """Process any queued messages when reconnecting"""
        if not self.connected:
            return
            
        processed = 0
        while not self.message_queue.empty():
            try:
                topic, payload, qos, retain = self.message_queue.get_nowait()
                self.client.publish(topic, payload, qos=qos, retain=retain)
                processed += 1
            except Exception as e:
                log(f"Error processing queued message: {e}", "error")
        
        if processed > 0:
            log(f"Processed {processed} queued messages")
    
    def publish(self, topic: str, payload: str, qos: int = None, retain: bool = None):
        """Publish message with queuing support"""
        # Use instance defaults if not specified
        if qos is None:
            qos = self.qos
        if retain is None:
            retain = self.retain
            
        if self.connected and self.client:
            try:
                result = self.client.publish(topic, payload, qos=qos, retain=retain)
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    log(f"Failed to publish to {topic}: {result.rc}", "error")
                    # Queue message for later
                    self.message_queue.put((topic, payload, qos, retain))
                return result
            except Exception as e:
                log(f"Error publishing to {topic}: {e}", "error")
                # Queue message for later
                self.message_queue.put((topic, payload, qos, retain))
        else:
            # Queue message for later
            self.message_queue.put((topic, payload, qos, retain))
            log(f"MQTT not connected - queued message for {topic}")
    
    def connect(self) -> bool:
        """Connect to MQTT broker with retry logic"""
        if not self.client:
            self.create_client()
        
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries and not self.connected:
            try:
                log(f"Connecting to MQTT broker {self.broker}:{self.port} (attempt {retry_count + 1}/{max_retries})")
                
                with self.connection_lock:
                    self.client.connect(self.broker, self.port, 60)
                    self.client.loop_start()
                
                # Wait for connection callback
                wait_time = 0
                while wait_time < 10 and not self.connected:
                    time.sleep(0.5)
                    wait_time += 0.5
                
                if self.connected:
                    log("MQTT connection established successfully")
                    return True
                else:
                    log("MQTT connection timeout - retrying...", "warning")
                    self.client.loop_stop()
                    retry_count += 1
                    
                    # Exponential backoff
                    delay = min(self.reconnect_delay * (2 ** retry_count), self.max_reconnect_delay)
                    log(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    
            except Exception as e:
                log(f"MQTT connection failed: {e}. Retrying in {self.reconnect_delay} seconds...", "error")
                retry_count += 1
                time.sleep(self.reconnect_delay)
        
        if not self.connected:
            log("Failed to connect to MQTT broker after maximum retries", "critical")
            return False
        
        return True
    
    def disconnect(self):
        """Cleanly disconnect from MQTT broker"""
        if self.connected:
            self._publish_status("offline", "shutdown")
            time.sleep(1)  # Allow status message to be sent
        
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                log("MQTT client disconnected")
            except Exception as e:
                log(f"Error during MQTT disconnect: {e}", "error")
        
        self.connected = False
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self.connected and self.client and self.client.is_connected()
    
    def send_heartbeat(self):
        """Send heartbeat to monitor connection health"""
        current_time = time.time()
        if current_time - self.last_heartbeat >= self.heartbeat_interval:
            if self.connected:
                self._publish_status("online", "heartbeat")
                self.last_heartbeat = current_time
            else:
                log("MQTT connection lost - attempting reconnection", "warning")
                self.connect()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MQTT connection statistics"""
        return {
            "connected": self.connected,
            "broker": f"{self.broker}:{self.port}",
            "topic": self.topic,
            "queued_messages": self.message_queue.qsize(),
            "last_heartbeat": datetime.fromtimestamp(self.last_heartbeat).isoformat() if self.last_heartbeat > 0 else "Never",
            "qos": self.qos,
            "retain": self.retain
        }
    
    def log_stats(self):
        """Log current MQTT statistics"""
        stats = self.get_stats()
        log(f"MQTT Stats: Connected={stats['connected']}, Broker={stats['broker']}, Queued={stats['queued_messages']}, QoS={stats['qos']}, Retain={stats['retain']}")



def main():
    log(f"Starting Airplanes Live Home Assistant Add-on v{get_addon_version()}")
    
    # Validate configuration first
    if not validate_config():
        log("Configuration validation failed. Please check your settings.", "critical")
        return
    
    log(f"Configuration: API_TYPE={API_TYPE}, API_URL={API_URL}, LAT={LATITUDE}, LON={LONGITUDE}, RADIUS={RADIUS}km ({RADIUS_NMI:.1f}nm)")
    log(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}, Topic: {MQTT_TOPIC}")
    
    mqtt_manager = MQTTManager(MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_manager.qos = MQTT_QOS
    mqtt_manager.retain = MQTT_RETAIN
    
    if not mqtt_manager.connect():
        log("Failed to connect to MQTT broker. Exiting.", "critical")
        return

    try:
        # Publish discovery once at startup
        if mqtt_manager.is_connected():
            publish_discovery(mqtt_manager)
            # Wait a moment for discovery to be processed
            time.sleep(3)
            # Publish initial data to help with discovery
            log("Publishing initial data for discovery...")
            initial_data = {
                "count": 0,
                "closest_lowest": "None",
                "closest_distance": "None",
                "highest": "None",
                "fastest_ground": 0,
                "fastest_air": 0,
                "aircraft_types": "None",
                "weather": "Unknown",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            mqtt_manager.publish(f"{MQTT_TOPIC}/summary", json.dumps(initial_data), retain=True)
            log("Initial data published")
        
        # Counter for periodic stats logging
        stats_counter = 0
        
        while True:
            data = fetch_airplane_data()
            if mqtt_manager.is_connected():
                publish_summary_data(mqtt_manager, data)
                publish_individual_aircraft(mqtt_manager, data)
                mqtt_manager.send_heartbeat() # Send heartbeat regularly
            else:
                log("MQTT not connected - skipping publish", "warning")
                mqtt_manager.send_heartbeat() # Still send heartbeat even if not connected
            
            # Log MQTT stats every 10 cycles
            stats_counter += 1
            if stats_counter % 10 == 0:
                mqtt_manager.log_stats()
            
            log(f"Sleeping for {UPDATE_INTERVAL} seconds")
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        log("Shutting down.")
    except Exception as e:
        log(f"Unexpected error: {e}", "critical")
    finally:
        mqtt_manager.disconnect()
        log("Cleanup completed")

if __name__ == "__main__":
    main()