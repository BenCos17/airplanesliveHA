# AirplanesLiveHA/app.py
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/api/airplanes', methods=['GET'])
def get_airplanes():
    # Here you would implement the logic to fetch airplane data
    return jsonify({"message": "Airplane data will be here."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)