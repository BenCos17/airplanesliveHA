# AirplanesLiveHA/app.py
from flask import Flask, jsonify, render_template
import requests
import os
import json

app = Flask(__name__)

def load_config():
    """Load configuration from Home Assistant options.json file"""
    config_path = "/data/options.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return {}

# Load configuration
config = load_config()

# Load configuration from options.json with fallback defaults
API_URL = config.get("api_url", "https://api.airplanes.live/v2/point")
LATITUDE = config.get("latitude", "53.2707")
LONGITUDE = config.get("longitude", "-9.0568")
RADIUS = config.get("radius", 50)

@app.route('/api/airplanes', methods=['GET'])
def get_airplanes():
    try:
        url = f"{API_URL}/{LATITUDE}/{LONGITUDE}/{RADIUS}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data from API: {e}")
        return jsonify({"error": "Failed to fetch data"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/airplane/<hex>', methods=['GET'])
def get_airplane(hex):
    try:
        # Use the hex endpoint from the API
        url = f"https://api.airplanes.live/v2/hex/{hex}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching airplane data: {e}")
        return jsonify({"error": "Failed to fetch data"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)







