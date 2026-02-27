# BME Sensor Server

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Note: this requires enabling I2C on your Raspberry Pi (`sudo raspi-config`).

## Running the Server

### Manual Start
Run the server using `uvicorn`:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Background Service Script
You can use the provided script to manage the server process:

```bash
./run_server.sh start   # Start server in background
./run_server.sh stop    # Stop the server
./run_server.sh status  # Check if running
./run_server.sh restart # Restart the server
```

- Logs are written to `server.log`.
- Process ID is stored in `server.pid`.

## API Endpoints

- **GET /**: Returns device status, uptime, and system info.
- **GET /latest**: Returns the most recent sensor reading.
- **GET /last/{num}**: Returns the last `num` readings (capped at history size, default 2000).

## Monitoring Tool

A client script `client_poller.py` is included to verify the sensor data and calculate simple statistics. This is useful for checking if the system is working correctly.

To use it:

1. Ensure all requirements are installed (including `pandas` and `requests`):
   ```bash
   pip install -r requirements.txt
   ```

2. Run the script:
   ```bash
   python3 client_poller.py
   ```

The script will fetch the last 1000 readings every 10 seconds and display:
- Current live readings depending on the latest timestamp.
- Min/Max/Mean temperature stats for each sensor over the requested window.

