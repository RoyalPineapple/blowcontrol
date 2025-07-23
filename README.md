![BlowControl_header](https://github.com/user-attachments/assets/896eb720-cef3-4280-a1e2-e0b479af587c)

# BlowControl

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/RoyalPineapple/blowcontrol/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/RoyalPineapple/blowcontrol/actions)
[![Codecov](https://codecov.io/gh/RoyalPineapple/blowcontrol/branch/master/graph/badge.svg)](https://codecov.io/gh/RoyalPineapple/blowcontrol)

A simple application for controlling Dyson fans via MQTT with support for real-time monitoring, async operations, and machine-readable JSON output.

## 🚀 Quick Start

### Option 1: Install as CLI App (Recommended)

1. **Install the package**:
   ```bash
   # Development installation (editable)
   pip install -e .

   # Or production installation
   pip install .
   ```

2. **Configure your device** (create `.env` file):
   ```bash
   DEVICE_IP=192.168.1.100
   MQTT_PORT=1883
   MQTT_PASSWORD=your-mqtt-password
   ROOT_TOPIC=XXX
   SERIAL_NUMBER=XXX-XX-XXXXXXXX
   ```

3. **Control your device**:
   ```bash
   # Basic control
   blowcontrol power on
   blowcontrol speed 5

   # Monitor state
   blowcontrol listen

   # Get JSON output for automation
   blowcontrol state --json
   ```

### Option 2: Run as Python Module

1. **Install dependencies**:
   ```bash
   pip install paho-mqtt python-dotenv
   ```

2. **Configure your device** (create `.env` file):
   ```bash
   DEVICE_IP=192.168.1.100
   MQTT_PORT=1883
   MQTT_PASSWORD=your-mqtt-password
   ROOT_TOPIC=XXX
   SERIAL_NUMBER=XXX-XX-XXXXXXXX
   ```

3. **Control your device**:
   ```bash
   # Basic control
   python3 -m blowcontrol power on
   python3 -m blowcontrol speed 5

   # Monitor state
   python3 -m blowcontrol listen

   # Get JSON output for automation
   python3 -m blowcontrol state --json
   ```

## 🔑 Getting Your Device Credentials

This project relies on **OpenDyson** to extract the necessary MQTT credentials from your Dyson device. OpenDyson is a Go-based client that can decrypt the device credentials needed for MQTT communication.

### Using OpenDyson

1. **Install OpenDyson**:
   ```bash
   # Option 1: Using go install (recommended)
   go install github.com/libdyson-wg/opendyson

   # Option 2: Download from releases
   # Visit: https://github.com/libdyson-wg/opendyson/releases
   # Download the executable for your OS and make it executable
   ```

2. **Login to your MyDyson account**:
   ```bash
   # First time setup - login to your MyDyson account
   opendyson login
   ```

3. **Extract your device credentials**:
   ```bash
   # List your devices and get credentials
   opendyson devices

   # This will output device information including:
   # - Device serial numbers
   # - IP addresses (if found on local network)
   # - MQTT credentials (username, password, topic root)
   ```

4. **Use the credentials in your `.env` file**:
   ```bash
   DEVICE_IP=192.168.1.100
   MQTT_PORT=1883
   MQTT_PASSWORD=[password-from-opendyson]
   ROOT_TOPIC=[topic-root-from-opendyson]
   SERIAL_NUMBER=[serial-number-from-opendyson]
   ```

### Additional OpenDyson Commands

```bash
# Listen to MQTT messages from your device
opendyson listen [SERIAL_NUMBER]

# Listen via cloud IoT service (if device not on local network)
opendyson listen [SERIAL_NUMBER] --iot

# Get help
opendyson help
```

### Security Note

⚠️ **Important**: The output from `opendyson devices` contains sensitive IoT credentials that allow remote control of your devices. **Never share this information** with anyone you don't trust completely.

## ✨ Features

- **🎛️ Device Control**: Power, fan speed, auto mode, night mode, sleep timer, oscillation, direction
- **📊 State Monitoring**: Real-time listening, on-demand state fetching
- **🤖 JSON Output**: Machine-readable responses for automation
- **🔧 Professional CLI**: Easy-to-use command-line interface

## 📖 Documentation

- **[App Documentation](./blowcontrol/README.md)**: Detailed usage guide, commands, and examples
- **[Game Plan](./blowcontrol/GAMEPLAN.md)**: Development roadmap and architecture notes
- **[Message Analysis](./blowcontrol/commands/dyson_message_analysis.md)**: Complete MQTT message reference

## 🏗️ Project Structure

```
blowcontrol/
├── blowcontrol/            # Main application
│   ├── commands/          # Individual command implementations
│   ├── mqtt/              # MQTT client and async operations
│   ├── state/             # Device state management
│   └── cli.py            # Command-line interface
├── experimentation/       # Research and protocol analysis
└── opendyson/            # Go-based Dyson client (submodule)
```

## 🔧 Commands Reference

| Command | Category | Syntax | Arguments | Description |
|---------|----------|--------|-----------|-------------|
| `power` | **Control** | `blowcontrol power <state>` | `on\|off` | Turn the fan ON or OFF |
| `auto` | **Control** | `blowcontrol auto <state>` | `on\|off` | Enable/disable auto mode |
| `night` | **Control** | `blowcontrol night <state>` | `on\|off` | Enable/disable night mode |
| `speed` | **Control** | `blowcontrol speed <speed>` | `0-10` | Set fan speed (0 turns off) |
| `timer` | **Control** | `blowcontrol timer <time>` | `0-540`, `2h15m`, `2:15`, `1h`, `45m` | Set sleep timer (0=off) |
| `listen` | **Monitoring** | `blowcontrol listen` | *(none)* | Real-time monitoring (Ctrl+C to exit) |
| `state` | **Monitoring** | `blowcontrol state [--json]` | `--json` (optional) | Fetch current state with optional JSON output |
| `width` | **Oscillation** | `blowcontrol width <width>` | `off\|narrow\|medium\|wide\|full` | Set oscillation width |
| `direction` | **Oscillation** | `blowcontrol direction <degrees>` | `0-359` | Set oscillation direction |
| `stop` | **Oscillation** | `blowcontrol stop` | *(none)* | Stop oscillation |

### Command Categories

- **🎛️ Control Commands**: Direct device control (power, settings, timers)
- **📊 Monitoring Commands**: State monitoring and real-time updates
- **🔄 Oscillation Commands**: Control fan oscillation and direction

### Quick Examples

```bash
# Basic control
blowcontrol power on                    # Turn fan on
blowcontrol speed 5                     # Set speed to 5
blowcontrol auto on                     # Enable auto mode
blowcontrol night on                    # Enable night mode
blowcontrol timer 2h15m                 # Set 2h15m sleep timer

# Oscillation control
blowcontrol width wide                  # Set wide oscillation
blowcontrol direction 180               # Point oscillation at 180°
blowcontrol stop                        # Stop oscillation

# Monitoring
blowcontrol listen                      # Real-time status updates
blowcontrol state --json                # Get current state as JSON

# Automation
blowcontrol power on --json             # JSON output for scripts
STATUS=$(blowcontrol state --json)      # Capture state in variable
```

## 🤖 Automation Examples

### Shell Scripting
```bash
# Morning routine
blowcontrol power on
blowcontrol auto on
blowcontrol speed 3

# Get current status
STATUS=$(blowcontrol state --json)
echo $STATUS | jq '.state.product-state.fpwr'
```

### Python Integration
```python
import json, subprocess

result = subprocess.run(['blowcontrol', 'state', '--json'],
                       capture_output=True, text=True)
state = json.loads(result.stdout)

if state['success']:
    print(f"Power: {state['state']['product-state']['fpwr']}")
```

## 🔍 Troubleshooting

- **Connection issues**: Verify `.env` configuration and network connectivity
- **No response**: Use `blowcontrol listen` to check device communication
- **JSON parsing**: Ensure you're using `--json` flag for machine-readable output
- **Command not found**: Make sure you've installed the package with `pip install -e .`

## 🏛️ Architecture

Built with modern Python practices:
- **Modular design** with clear separation of concerns
- **Async/await support** using `asyncio.to_thread()`
- **Thread-safe operations** for concurrent access
- **Comprehensive error handling** with structured responses
- **Professional CLI** with argparse and proper exit codes

## 🛠️ Development

### CI/CD Pipeline
This project uses GitHub Actions for continuous integration and deployment:

- **Automated Testing**: Runs on Python 3.9 and 3.11
- **Code Quality**: Black formatting, isort imports, flake8 linting, mypy type checking
- **Security Analysis**: Bandit security scanning and dependency vulnerability checks
- **Coverage Reporting**: Codecov integration for test coverage tracking

### Local Development Setup
```bash
# Clone and setup
git clone https://github.com/RoyalPineapple/blowcontrol.git
cd blowcontrol

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run code quality checks
pre-commit run --all-files
```

### Pre-commit Hooks
The repository includes pre-commit hooks that automatically check for:
- Trailing whitespace
- Missing newlines at end of files
- Debug statements
- Merge conflict markers
- Code formatting (black)
- Import sorting (isort)
- Code style (flake8)

The hooks run automatically on every commit, ensuring code quality.

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Code style and standards
- Testing requirements
- Pull request process
- Development workflow

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **paho-mqtt**: Eclipse Public License v1.0 / Eclipse Distribution License v1.0
- **python-dotenv**: BSD-3-Clause License
- **pytest**: MIT License
- **pytest-cov**: MIT License
- **pytest-mock**: MIT License
- **pytest-asyncio**: Apache License 2.0

---

**Now you're ready to control your Dyson device like a total fool!** 🌪️

## 📚 Documentation

- **[App Documentation](./blowcontrol/README.md)** - Detailed usage, architecture, and examples
- **[Message Analysis](./blowcontrol/commands/dyson_message_analysis.md)** - Complete MQTT message reference
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines and setup
- **[Changelog](CHANGELOG.md)** - Version history and changes
