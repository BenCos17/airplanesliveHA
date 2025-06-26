# AirplanesLiveHA/app.py
from flask import Flask, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Load configuration from environment variables (Home Assistant add-on standard)
API_URL = os.getenv("API_URL", "https://api.airplanes.live/v2/point")
LATITUDE = os.getenv("LATITUDE", "53.2707")
LONGITUDE = os.getenv("LONGITUDE", "-9.0568")
RADIUS = os.getenv("RADIUS", "50")

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







