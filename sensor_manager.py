import smbus2
import bme280
import time
import threading
from collections import deque
from datetime import datetime
import copy

# Constants
MUX_ADDR = 0x70
BME_ADDRS = [0x76, 0x77]

class SensorManager:
    def __init__(self, bus_number=1, history_size=2000, poll_interval=2.0):
        self.bus_number = bus_number
        self.bus = None
        self.history_size = history_size
        self.poll_interval = poll_interval
        
        self.readings = deque(maxlen=self.history_size)
        self.lock = threading.Lock()
        
        self._stop_event = threading.Event()
        self._thread = None
        
        self._initialize_bus()
    
    def start_polling(self):
        if self._thread is not None and self._thread.is_alive():
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._thread.start()
        print("Sensor polling started.")

    def stop_polling(self):
        if self._thread is None or not self._thread.is_alive():
            return
            
        self._stop_event.set()
        self._thread.join(timeout=5.0)
        print("Sensor polling stopped.")

    def _polling_loop(self):
        while not self._stop_event.is_set():
            start_time = time.time()
            data = self._fetch_sensor_data()
            
            with self.lock:
                self.readings.append(data)
            
            # Calculate sleep time to maintain interval
            elapsed = time.time() - start_time
            sleep_time = max(0, self.poll_interval - elapsed)
            
            # Sleep in small chunks to allow quick shutdown
            if sleep_time > 0:
                self._stop_event.wait(sleep_time)

    def get_latest_reading(self):
        with self.lock:
            if not self.readings:
                return None
            return copy.deepcopy(self.readings[-1])

    def get_last_n_readings(self, n: int):
        with self.lock:
            if not self.readings:
                return []
            # deque slicing isn't direct, convert to list
            # list(self.readings) creates a copy, then slice
            all_readings = list(self.readings)
            return all_readings[-n:]


    def _initialize_bus(self):
        try:
            self.bus = smbus2.SMBus(self.bus_number)
        except Exception as e:
            print(f"Error initializing I2C bus: {e}")
            self.bus = None

    def _enable_mux_channel(self, channel):
        if self.bus is None:
            return False
        if channel < 0 or channel > 7:
            return False
        try:
            self.bus.write_byte(MUX_ADDR, 1 << channel)
            time.sleep(0.01)  # Settling time
            return True
        except Exception as e:
            # print(f"Error switching Mux to channel {channel}: {e}")
            return False

    def _disable_mux(self):
        if self.bus is None:
            return
        try:
            self.bus.write_byte(MUX_ADDR, 0x00)
        except Exception:
            pass

    def _fetch_sensor_data(self):
        read_start_time = time.time()
        if self.bus is None:
            self._initialize_bus()
            if self.bus is None:
               return {"error": "I2C bus unavailable", "timestamp": datetime.now().isoformat()}

        # Dictionary to hold data: channel -> address -> data
        channels_data = {}
        
        # Scan all 8 channels of the Mux
        for channel in range(8):
            if not self._enable_mux_channel(channel):
                continue

            per_channel_sensors = {}
            
            for addr in BME_ADDRS:
                try:
                    # Try reading calibration params to confirm device presence and readiness
                    calibration_params = bme280.load_calibration_params(self.bus, addr)
                    data = bme280.sample(self.bus, addr, calibration_params)
                    
                    per_channel_sensors[hex(addr)] = {
                        "temperature_c": round(data.temperature, 2),
                        "pressure_hpa": round(data.pressure, 2),
                        "humidity_rh": round(data.humidity, 2)
                    }
                except OSError:
                    # Device not found at this address
                    pass
                except Exception as e:
                    # Maybe print for debugging but don't crash
                    pass
            
            # Only add the channel key if we actually found sensors
            if per_channel_sensors:
                channels_data[f"channel_{channel}"] = per_channel_sensors

        return {
            "timestamp": datetime.now().isoformat(),
            "timetaken": time.time() - read_start_time,
            "channels": channels_data
        }

    def cleanup(self):
        if self.bus:
            self.bus.close()
