![BlowControl_header](https://github.com/user-attachments/assets/896eb720-cef3-4280-a1e2-e0b479af587c)

# BlowControl

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/RoyalPineapple/blowcontrol/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/RoyalPineapple/blowcontrol/actions)
[![Codecov](https://codecov.io/gh/RoyalPineapple/blowcontrol/branch/master/graph/badge.svg)](https://codecov.io/gh/RoyalPineapple/blowcontrol)

**BlowControl** is a command-line app for controlling Dyson fans over MQTT. It is built hastily and without an excess of care, but it works. You get device control, state monitoring, async operations, and machine-readable JSON output for automation. If you need a rock solid, enterprise-grade solution, keep looking. If your goal is to change the fan settings without ever moving your cursor from the active terminal window, this is your stop.

---

## 🚀 Quick Start

1. **Install**
   ```bash
   pip install -e .   # Dev mode
   # or
   pip install .      # Standard
   ```

2. **Configure** (create a `.env` file):
   ```ini
   DEVICE_IP=192.168.1.100
   MQTT_PORT=1883
   MQTT_PASSWORD=your-mqtt-password
   ROOT_TOPIC=XXX
   SERIAL_NUMBER=XXX-XX-XXXXXXXX
   ```

3. **Control your device**:
   ```bash
   blowcontrol power on
   blowcontrol speed 5
   blowcontrol listen
   blowcontrol state --json
   ```
   > **Note:** All commands support the `--json` flag for machine-readable output. Scripting is expected.

---

## 🔑 Getting Device Credentials

You’ll need MQTT credentials from your Dyson device. Dyson doesn’t make this easy. Use [OpenDyson](https://github.com/libdyson-wg/opendyson):

```bash
# Install OpenDyson (requires Go)
 go install github.com/libdyson-wg/opendyson

# Log in and extract credentials
 opendyson login
 opendyson devices
```

Copy the credentials into your `.env` file. Don’t lose them.

---

## ✨ Features

- Control your Dyson fan: power, speed, auto mode, night mode, sleep timer, oscillation, direction
- State monitoring: real-time and on-demand
- Universal `--json` output for all commands
- Async/await support for non-blocking operations
- CLI with argparse and proper exit codes

---

## 📖 Command Reference

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

> **All commands support `--json` for machine-readable output.**

---

## ⚡ Quick Examples

```bash
# Basic control
blowcontrol power on
blowcontrol speed 5
blowcontrol auto on
blowcontrol night on
blowcontrol timer 2h15m

# Oscillation
blowcontrol width wide
blowcontrol direction 180
blowcontrol stop

# Monitoring
blowcontrol listen
blowcontrol state --json

# Automation
blowcontrol power on --json
STATUS=$(blowcontrol state --json)
```

### Python Integration
```python
import json, subprocess
result = subprocess.run(['blowcontrol', 'state', '--json'], capture_output=True, text=True)
state = json.loads(result.stdout)
if state['success']:
    print(f"Power: {state['state']['product-state']['fpwr']}")
```

---

## 🛠️ Troubleshooting
- **Connection issues**: Check `.env` and your network.
- **No response**: Use `blowcontrol listen` to see if your fan is even listening.
- **JSON parsing**: Use `--json` and pipe to `jq` or similar. If it’s weird, it’s probably the fan.
- **Command not found**: Did you install it? Try `pip install -e .`.

---

## 🏗️ Development & Contributing
- See [CONTRIBUTING.md](CONTRIBUTING.md) for code style, PR process, and dev setup
- See [tests/README.md](tests/README.md) for test suite usage and patterns
- Run tests: `pytest tests/`
- Run code quality checks: `pre-commit run --all-files`

---

## 📄 License
MIT License. See [LICENSE](LICENSE).

---

**Now you can control your Dyson device from the terminal. Don’t blame me if it blows up.**

## 📚 More Documentation
- [App Documentation](./blowcontrol/README.md) - Internal usage, architecture, and extending
- [Message Analysis](./blowcontrol/commands/dyson_message_analysis.md) - MQTT message reference
- [Changelog](CHANGELOG.md) - Version history and changes
