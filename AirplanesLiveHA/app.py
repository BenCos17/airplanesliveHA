# AirplanesLiveHA/app.py
from flask import Flask, jsonify, render_template
import requests
import os

app = Flask(__name__)

API_URL = "http://api.airplanes.live/v2/"  # Set your API URL here

@app.route('/api/airplanes', methods=['GET'])
def get_airplanes():
    # Fetch airplane data from the Airplanes.live API
    response = requests.get(f"{API_URL}/mil")  # Example endpoint for military aircraft
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
    response = requests.get(f"{API_URL}/hex/{hex}")
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)