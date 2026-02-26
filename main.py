import time
import socket
import platform
from fastapi import FastAPI
from sensor_manager import SensorManager
from datetime import datetime, timedelta

app = FastAPI()
sensor_manager = SensorManager()

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(timedelta(seconds=uptime_seconds))
    except:
        return "Unknown"

@app.get("/")
def read_root():
    routes = [
        {"path": route.path, "name": route.name, "methods": list(route.methods)}
        for route in app.routes
    ]
    return {
        "device_name": socket.gethostname(),
        "system": platform.system(),
        "release": platform.release(),
        "uptime": get_uptime(),
        "status": "online",
        "description": "BME280 Sensor Server via PCA9548 I2C Mux",
        "endpoints": routes
    }

@app.get("/currentreadings")
def read_current_readings():
    return sensor_manager.get_all_readings()

# To run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
