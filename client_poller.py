import requests
import pandas as pd
import time
import os
from datetime import datetime

# --- SETTINGS ---
N_SAMPLES = 1000         # Number of samples to look back for stats
INTERVAL = 10           # Refresh every X seconds
URL = f"https://access-bme-data.hamzaanver.com/last/{N_SAMPLES}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_data():
    # Adding a unique timestamp '?t=' forces the server to bypass any cache
    cache_buster = int(time.time())
    response = requests.get(f"{URL}?t={cache_buster}")
    return response.json()

def process_readings(data):
    rows = []
    for r in data['readings']:
        # Flattening the nested JSON
        ts = r['timestamp']
        for ch_name, ch_data in r['channels'].items():
            for addr, sensors in ch_data.items():
                rows.append({
                    'timestamp': ts,
                    'sensor': f"{ch_name}_{addr}",
                    'temp': sensors['temperature_c'],
                    'press': sensors['pressure_hpa'],
                    'hum': sensors['humidity_rh']
                })
    return pd.DataFrame(rows)

print("Starting Live Monitor... (Ctrl+C to stop)")

try:
    while True:
        try:
            raw_data = fetch_data()
            df = process_readings(raw_data)
            
            # 1. Get the very latest readings (the last sample in the response)
            latest_ts = df['timestamp'].iloc[-1]
            current_readings = df[df['timestamp'] == latest_ts]
            
            # 2. Calculate Stats over the last N samples
            stats = df.groupby('sensor')['temp'].agg(['min', 'max', 'mean'])
            stats['max_deviation'] = stats['max'] - stats['min']
            
            # --- DISPLAY ---
            clear_screen()
            print(f"--- BME LIVE MONITOR | {datetime.now().strftime('%H:%M:%S')} ---")
            print(f"Requesting last {N_SAMPLES} samples every {INTERVAL}s")
            print(f"Received {raw_data.get('count', '?')} readings (Requested: {raw_data.get('requested', '?')})\n")
            
            print("CURRENT READINGS:")
            print(current_readings[['sensor', 'temp', 'press', 'hum']].to_string(index=False))
            
            print("\nTEMPERATURE STATS (Last n samples):")
            print(stats.round(3).to_string())
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nMonitor stopped by user.")