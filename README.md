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
- **GET /currentreadings**: Returns JSON object with sensor readings.
  - Structure:
    ```json
    {
      "timestamp": "2023-10-27T10:00:00.123456",
      "channels": {
        "channel_0": {
          "0x76": { "temperature_c": 25.4, ... },
          "0x77": { "temperature_c": 26.1, ... }
        },
        ...
      }
    }
    ```
