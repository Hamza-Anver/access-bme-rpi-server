import time
import socket
import platform
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sensor_manager import SensorManager
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

sensor_manager = SensorManager(poll_interval=2.0, history_size=10000)

@asynccontextmanager
async def lifespan(app: FastAPI):
    sensor_manager.start_polling()
    yield
    sensor_manager.stop_polling()

app = FastAPI(lifespan=lifespan)

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
        if isinstance(route, APIRoute)
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

@app.get("/latest")
def read_current_readings():
    reading = sensor_manager.get_latest_reading()
    if reading is None:
        return {"status": "Waiting for sensor data..."}
    return reading

@app.get("/last/{num}")
def read_last_readings(num: int):
    # Limit requests to history size
    safe_num = min(num, sensor_manager.history_size)
    safe_num = max(safe_num, 1)
    
    readings = sensor_manager.get_last_n_readings(safe_num)
    return {
        "count": len(readings),
        "requested": num,
        "readings": readings
    }


# To run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
