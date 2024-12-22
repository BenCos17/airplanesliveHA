# AirplanesLiveHA/app.py
from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/api/airplanes', methods=['GET'])
def get_airplanes():
    # Replace with actual logic to fetch airplane data
    api_url = "YOUR_API_URL_HERE"  # Replace with the actual API URL
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()  # Assuming data contains a list of airplanes with lat/lon
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)