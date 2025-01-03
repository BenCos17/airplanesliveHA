# AirplanesLiveHA/app.py
from flask import Flask, jsonify, render_template
import requests
import os
import yaml  # Import yaml to read the config file

app = Flask(__name__)

# Load configuration from @config.yaml
def load_config():
    config_path = '/config/@config.yaml'  # Path to the config file
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Fetch configuration
config = load_config()

# Set your actual API URL here
api_url = "http://api.airplanes.live/v2/"  # Ensure this is correct

# Configuration for API URLs
API_URLS = [
    f"{api_url}/mil",  # Military aircraft
    f"{api_url}/ladd",  # LADD aircraft
    f"{api_url}/pia",   # PIA aircraft
    f"{api_url}/hex/[hex]",  # Replace [hex] with actual hex ID
    f"{api_url}/callsign/[callsign]",  # Replace [callsign] with actual callsign
    f"{api_url}/reg/[reg]",  # Replace [reg] with actual registration
    f"{api_url}/type/[type]",  # Replace [type] with actual ICAO type code
    f"{api_url}/squawk/[squawk]",  # Replace [squawk] with actual squawk code
    f"{api_url}/point/[lat]/[lon]/[radius]"  # Replace [lat], [lon], and [radius] with actual values
]

@app.route('/api/airplanes', methods=['GET'])
def get_airplanes():
    try:
        response = requests.get(API_URLS[0])  # Example endpoint for military aircraft
        response.raise_for_status()  # Raise an error for bad responses
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
    response = requests.get(f"{api_url}/hex/{hex}")
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

