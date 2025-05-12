from flask import Flask, jsonify
from datetime import datetime
import socket
import requests

app = Flask(__name__)

DHAKA_COORDS = {
    "latitude": 23.8103,
    "longitude": 90.4125
}

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_dhaka_weather():
    try:
        params = {
            "latitude": DHAKA_COORDS["latitude"],
            "longitude": DHAKA_COORDS["longitude"],
            "current_weather": True
        }
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        temperature = data["current_weather"]["temperature"]
        return {"temperature": str(temperature), "temp_unit": "c"}
    except Exception as e:
        return {"error": "Could not fetch weather", "details": str(e)}


@app.route("/api/hello", methods=["GET"])
def hello():
    hostname = socket.gethostname()
    dt = datetime.utcnow().strftime("%y%m%d%H%M")
    weather = fetch_dhaka_weather()

    data = {
        "hostname": hostname,
        "datetime": dt,
        "version": "1.0.0",
        "weather": {
            "dhaka": weather
        }
    }
    return jsonify(data)


@app.route("/api/health", methods=["GET"])
def health():
    try:
        # Basic call to Open-Meteo to verify reachability
        response = requests.get(
            WEATHER_API_URL,
            params={
                "latitude": DHAKA_COORDS["latitude"],
                "longitude": DHAKA_COORDS["longitude"],
                "current_weather": True
            },
            timeout=5
        )
        if response.status_code == 200:
            return jsonify({"status": "healthy", "weather_api": "reachable"}), 200
        else:
            return jsonify({"status": "unhealthy", "weather_api": "unreachable"}), 503
    except Exception:
        return jsonify({"status": "unhealthy", "weather_api": "unreachable"}), 503


if __name__ == "__main__":
    app.run(debug=True)
