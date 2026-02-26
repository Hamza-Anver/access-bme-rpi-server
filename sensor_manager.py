import smbus2
import bme280
import time
from datetime import datetime

# Constants
MUX_ADDR = 0x70
BME_ADDRS = [0x76, 0x77]

class SensorManager:
    def __init__(self, bus_number=1):
        self.bus_number = bus_number
        self.bus = None
        self._initialize_bus()

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

    def get_all_readings(self):
        if self.bus is None:
            self._initialize_bus()
            if self.bus is None:
               return {"error": "I2C bus unavailable"}

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
            "channels": channels_data
        }

    def cleanup(self):
        if self.bus:
            self.bus.close()
