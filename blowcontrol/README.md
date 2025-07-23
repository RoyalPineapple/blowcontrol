# BlowControl Modular App

## Overview

A modular, professional-quality command-line app for controlling Dyson fans over MQTT. Supports device control, state monitoring, and both synchronous and asynchronous operations with machine-readable JSON output.

---

## Features

✅ **Device Control**: Power, auto mode, night mode, fan speed, sleep timer
✅ **State Monitoring**: Real-time listening, on-demand state fetching
✅ **Async Support**: Non-blocking operations with async/await
✅ **JSON Output**: Machine-readable responses for automation
✅ **Background Listeners**: Thread-safe state monitoring
✅ **Clean CLI**: Professional command-line interface with helpful output

---

## Configuration

This app uses environment variables for configuration. The easiest way to set these is with a `.env` file in your project root:

```
# BlowControl .env configuration example
DEVICE_IP=192.168.3.82
MQTT_PORT=1883
MQTT_PASSWORD=your-mqtt-password
ROOT_TOPIC=438M
SERIAL_NUMBER=9HC-EU-UDB6777A
```

- `DEVICE_IP`: Dyson device IP address (required)
- `MQTT_PORT`: MQTT port (default: 1883)
- `MQTT_PASSWORD`: MQTT password (from OpenDyson)
- `ROOT_TOPIC`: MQTT root topic (from OpenDyson, often a short code)
- `SERIAL_NUMBER`: Dyson device serial number (from OpenDyson, also used as MQTT username)

The app will automatically load these from `.env` if present.

---

## Installation

- Install Python 3.8+
- Install dependencies:
  ```sh
  pip install paho-mqtt python-dotenv
  ```

---

## Usage

Run the CLI using:

```
python3 -m app <command> [arguments]
```

## 🔧 Basic Usage

```bash
# Power control
python3 -m app power on|off

# Fan settings
python3 -m app speed 0-10
python3 -m app auto on|off
python3 -m app night on|off
python3 -m app timer 2h15m|off

# Oscillation
python3 -m app width off|narrow|medium|wide|full
python3 -m app direction 0-359

# Monitoring
python3 -m app listen
python3 -m app state [--json]
```

**JSON Output Example:**
```json
{
  "success": true,
  "state": {
    "msg": "CURRENT-STATE",
    "time": "2025-07-22T17:44:55.000Z",
    "product-state": {
      "fpwr": "ON",
      "fnsp": "0005",
      "auto": "OFF",
      "nmod": "OFF",
      "oson": "OFF"
    }
  },
  "environmental": {
    "msg": "ENVIRONMENTAL-CURRENT-SENSOR-DATA",
    "data": {
      "pm25": "0106",
      "pm10": "0093"
    }
  }
}
```

---

## Automation & Scripting

### Shell Scripting
```sh
#!/bin/bash
# Morning routine
python3 -m app power on
python3 -m app speed 3
python3 -m app auto on

# Check status
python3 -m app state --json | jq '.state.product-state.fpwr'
```

### JSON Processing
```sh
# Get current fan speed
SPEED=$(python3 -m app state --json | jq -r '.state.product-state.fnsp')

# Check if auto mode is enabled
AUTO=$(python3 -m app state --json | jq -r '.state.product-state.auto')
```

### Python Integration
```python
import json
import subprocess

# Get device state
result = subprocess.run(['python3', '-m', 'app', 'state', '--json'],
                       capture_output=True, text=True)
state = json.loads(result.stdout)

if state['success']:
    power = state['state']['product-state']['fpwr']
    fan_speed = state['state']['product-state']['fnsp']
    print(f"Power: {power}, Speed: {fan_speed}")
```

---

## Architecture

The app is designed with a modular architecture:

- **`app/commands/`**: Individual command implementations
- **`app/mqtt/`**: MQTT client and async wrapper
- **`app/state/`**: Device state management and printing
- **`app/cli.py`**: Command-line interface
- **`app/config.py`**: Configuration management

### Key Components

- **`DysonMQTTClient`**: Synchronous MQTT operations
- **`async_get_state()`**: Asynchronous state fetching
- **`DeviceStatePrinter`**: Formatted output for human consumption

---

## Extending

### Adding New Commands
1. Create a new module in `app/commands/`
2. Implement your command function
3. Add CLI integration in `app/cli.py`
4. Add tests in the same directory

### Custom State Processing
- Extend `DeviceStatePrinter` for custom output formats
- Use the JSON output mode for programmatic processing

---

## Troubleshooting

### Connection Issues
- Ensure your `.env` file has correct values
- Verify the device is on your network and accessible
- Check that MQTT credentials from OpenDyson are correct

### Command Not Responding
- Use `python3 -m app listen` to see if device is sending messages
- Check logs for connection errors

### JSON Parsing
- Ensure you're using `--json` flag for machine-readable output
- Pipe output through `jq` to validate JSON structure
- Check the `success` field in JSON responses for error handling

---

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
