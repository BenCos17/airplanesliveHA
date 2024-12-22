# AirplanesLiveHA/app.py
from flask import Flask, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Load the configuration from the environment variables
api_url = os.getenv('API_URL', 'http://api.airplanes.live/v2/')  # Default to the API URL if not set

@app.route('/api/airplanes', methods=['GET'])
def get_airplanes():
    # Fetch airplane data from the Airplanes.live API
    response = requests.get(f"{api_url}/mil")  # Example endpoint for military aircraft
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code

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