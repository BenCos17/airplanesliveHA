# AirplanesLiveHA/app.py
from flask import Flask, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Set your actual API URL here
api_url = "http://api.airplanes.live/v2/"  # Ensure this is correct

@app.route('/api/airplanes', methods=['GET'])
def get_airplanes():
    try:
        response = requests.get(f"{api_url}/mil")  # Example endpoint for military aircraft
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

