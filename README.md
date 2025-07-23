![BlowControl_header](https://github.com/user-attachments/assets/896eb720-cef3-4280-a1e2-e0b479af587c)

# BlowControl

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/RoyalPineapple/blowcontrol/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/RoyalPineapple/blowcontrol/actions)
[![Codecov](https://codecov.io/gh/RoyalPineapple/blowcontrol/branch/master/graph/badge.svg)](https://codecov.io/gh/RoyalPineapple/blowcontrol)

**BlowControl** is a hacky, irreverent command-line app for bossing your Dyson fan around via MQTT. Vibe-coded in a caffeine-fueled 48-hour sprint, it’s held together by zip ties, hope, and a lot of `--json` output. If you want a “professional” solution, look elsewhere—this is for tinkerers, automation goblins, and people who like yelling at their appliances from the terminal.

---

## 🚀 Quick Start (No Warranty, No Regrets)

1. **Install**
   ```bash
   pip install -e .   # For the reckless
   # or
   pip install .      # For the slightly less reckless
   ```

2. **Configure** (make a `.env` file, pray to the IoT gods):
   ```ini
   DEVICE_IP=192.168.1.100
   MQTT_PORT=1883
   MQTT_PASSWORD=your-mqtt-password
   ROOT_TOPIC=XXX
   SERIAL_NUMBER=XXX-XX-XXXXXXXX
   ```

3. **Boss your fan around**:
   ```bash
   blowcontrol power on
   blowcontrol speed 5
   blowcontrol listen
   blowcontrol state --json
   ```
   > **Note:** All commands support the `--json` flag for machine-readable output—because who doesn’t want to parse their fan’s feelings in a shell script?

---

## 🔑 Getting Device Credentials (The Annoying Part)

You’ll need MQTT credentials from your Dyson device. Dyson doesn’t want you to have them, but [OpenDyson](https://github.com/libdyson-wg/opendyson) exists:

```bash
# Install OpenDyson (Go required, sorry)
 go install github.com/libdyson-wg/opendyson

# Log in and extract your precious secrets
 opendyson login
 opendyson devices
```

Copy the credentials into your `.env` file and try not to leak them on Twitter.

---

## ✨ Features (Such As They Are)

- Tell your Dyson fan what to do: power, speed, auto mode, night mode, sleep timer, oscillation, direction
- Spy on your fan’s state: real-time and on-demand
- Universal `--json` output for all commands (robots love it)
- Async/await support so your scripts don’t block and you can feel modern
- CLI with argparse and proper exit codes (sometimes)

---

## 📖 Command Reference (You’ll Forget These)

| Command      | Category      | Syntax                                 | Arguments                | Description                        |
|--------------|--------------|----------------------------------------|--------------------------|------------------------------------|
| `power`      | Control       | `blowcontrol power <state>`            | `on|off`                 | Turn the fan ON or OFF             |
| `auto`       | Control       | `blowcontrol auto <state>`             | `on|off`                 | Enable/disable auto mode           |
| `night`      | Control       | `blowcontrol night <state>`            | `on|off`                 | Enable/disable night mode          |
| `speed`      | Control       | `blowcontrol speed <speed>`            | `0-10`                   | Set fan speed (0 turns off)        |
| `timer`      | Control       | `blowcontrol timer <time>`             | `0-540`, `2h15m`, etc.   | Set sleep timer (0=off)            |
| `listen`     | Monitoring    | `blowcontrol listen`                   | *(none)*                 | Real-time monitoring               |
| `state`      | Monitoring    | `blowcontrol state [--json]`           | `--json` (optional)      | Fetch current state                |
| `width`      | Oscillation   | `blowcontrol width <width>`            | `off|narrow|medium|wide|full` | Set oscillation width        |
| `direction`  | Oscillation   | `blowcontrol direction <degrees>`      | `0-359`                  | Set oscillation direction          |
| `stop`       | Oscillation   | `blowcontrol stop`                     | *(none)*                 | Stop oscillation                   |

> **All commands support `--json` for machine-readable output.**

---

## ⚡ Quick Examples (Copy, Paste, Hope)

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

### Python Integration (Because Why Not)
```python
import json, subprocess
result = subprocess.run(['blowcontrol', 'state', '--json'], capture_output=True, text=True)
state = json.loads(result.stdout)
if state['success']:
    print(f"Power: {state['state']['product-state']['fpwr']}")
```

---

## 🛠️ Troubleshooting (You’ll Need This)
- **Connection issues**: Check `.env` and network. Or just reboot everything.
- **No response**: Use `blowcontrol listen` to see if your fan is ghosting you.
- **JSON parsing**: Use `--json` and pipe to `jq` or similar. Blame the fan if it’s weird.
- **Command not found**: Did you actually install it? Try `pip install -e .`.

---

## 🏗️ Development & Contributing (You Maniac)
- See [CONTRIBUTING.md](CONTRIBUTING.md) for code style, PR process, and dev setup
- See [tests/README.md](tests/README.md) for test suite usage and patterns
- Run tests: `pytest tests/`
- Run code quality checks: `pre-commit run --all-files`

---

## 📄 License
MIT License. See [LICENSE](LICENSE).

---

**Now you're ready to control your Dyson device like a total fool!** 🌪️

## 📚 More Documentation
- [App Documentation](./blowcontrol/README.md) - Internal usage, architecture, and extending
- [Message Analysis](./blowcontrol/commands/dyson_message_analysis.md) - MQTT message reference
- [Changelog](CHANGELOG.md) - Version history and changes
