
**BlowControl** is a command-line tool for controlling Dyson fans over MQTT. It is built hastily and without an excess of care but it seems to work. You get device control, state monitoring, async operations, and machine-readable JSON output for automation. If you need a rock solid, enterprise-grade solution, keep looking. If your goal is to change the fan settings without ever moving your cursor from the active terminal window, this is your stop.

---

## Features

✅ **Device Control**: Power, auto mode, night mode, fan speed, sleep timer
✅ **State Monitoring**: Real-time listening, on-demand state fetching
✅ **Async Support**: Non-blocking operations with async/await...
✅ **JSON Output**: Machine-readable responses for automation
✅ **Background Listeners**: Hopefully thread-safe state monitoring
✅ **Clean Looking CLI**: Professional looking command-line interface with helpful output sells the quality

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

## Command Reference

| Command      | Category      | Syntax                                 | Arguments                | Description                        |
|--------------|--------------|----------------------------------------|--------------------------|------------------------------------|
| `power`      | Control       | `blowcontrol power <state>`            | `on|off`, `true|false`   | Turn the fan ON or OFF             |
| `auto`       | Control       | `blowcontrol auto <state>`             | `on|off`, `true|false`   | Enable/disable auto mode           |
| `night`      | Control       | `blowcontrol night <state>`            | `on|off`, `true|false`   | Enable/disable night mode          |
| `speed`      | Control       | `blowcontrol speed <speed>`            | `0-10`                   | Set fan speed (0 turns off)        |
| `timer`      | Control       | `blowcontrol timer <time>`             | `0-540`, `2h15m`, etc.   | Set sleep timer (0=off)            |
| `listen`     | Monitoring    | `blowcontrol listen`                   | *(none)*                 | Real-time monitoring               |
| `state`      | Monitoring    | `blowcontrol state         `           | *(none)*                 | Fetch current state                |
| `width`      | Oscillation   | `blowcontrol width <width>`            | `off|narrow|medium|wide|full` | Set oscillation width        |
| `direction`  | Oscillation   | `blowcontrol direction <degrees>`      | `0-359`                  | Set oscillation direction          |

---

## Automation & Scripting

### Shell Scripting
```sh
#!/bin/bash
# Morning routine
blowcontrol power on
blowcontrol speed 3
blowcontrol auto on

# Check status
blowcontrol state --json | jq '.state.product-state.fpwr'
```

### JSON Processing
```sh
# Get current fan speed
SPEED=$(blowcontrol state --json | jq -r '.state.product-state.fnsp')

# Check if auto mode is enabled
AUTO=$(blowcontrol state --json | jq -r '.state.product-state.auto')
```

### Python Integration
```python
import json
import subprocess

# Get device state
result = subprocess.run(['blowcontrol', 'state', '--json'],
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

- **`blowcontrol/commands/`**: Individual command implementations
- **`blowcontrol/mqtt/`**: MQTT client and async wrapper
- **`blowcontrol/state/`**: Device state management and printing
- **`blowcontrol/cli.py`**: Command-line interface
- **`blowcontrol/config.py`**: Configuration management

### Key Components

- **`DysonMQTTClient`**: Synchronous MQTT operations
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
- Use `blowcontrol listen` to see if device is sending messages
- Check logs for connection errors

### JSON Parsing
- Ensure you're using `--json` flag for machine-readable output
- Pipe output through `jq` to validate JSON structure
- Check the `success` field in JSON responses for error handling

---

## License

This project is licensed under the Seems to Work License - see the [LICENSE](../LICENSE) file for details.
