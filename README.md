# Dyson2MQTT

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/RoyalPineapple/dyson2mqtt/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/RoyalPineapple/dyson2mqtt/actions)
[![Codecov](https://codecov.io/gh/RoyalPineapple/dyson2mqtt/branch/master/graph/badge.svg)](https://codecov.io/gh/RoyalPineapple/dyson2mqtt)

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
   DEVICE_IP=192.168.3.82
   MQTT_PORT=1883
   MQTT_PASSWORD=your-mqtt-password
   ROOT_TOPIC=XXX
   SERIAL_NUMBER=XXX-XX-XXXXXXXX
   ```

3. **Control your device**:
   ```bash
   # Basic control
   dyson2mqtt power on
   dyson2mqtt speed 5

   # Monitor state
   dyson2mqtt listen

   # Get JSON output for automation
   dyson2mqtt state --json
   ```

### Option 2: Run as Python Module

1. **Install dependencies**:
   ```bash
   pip install paho-mqtt python-dotenv
   ```

2. **Configure your device** (create `.env` file):
   ```bash
   DEVICE_IP=192.168.3.82
   MQTT_PORT=1883
   MQTT_PASSWORD=your-mqtt-password
   ROOT_TOPIC=XXX
   SERIAL_NUMBER=XXX-XX-XXXXXXXX
   ```

3. **Control your device**:
   ```bash
   # Basic control
   python3 -m dyson2mqtt power on
   python3 -m dyson2mqtt speed 5

   # Monitor state
   python3 -m dyson2mqtt listen

   # Get JSON output for automation
   python3 -m dyson2mqtt state --json
   ```

## 🔑 Getting Your Device Credentials

This project relies on **OpenDyson** to extract the necessary MQTT credentials from your Dyson device. OpenDyson is a Go-based client that can decrypt the device credentials needed for MQTT communication.

### Using OpenDyson

1. **Install OpenDyson**:
   ```bash
   # Clone the OpenDyson repository
   git clone https://github.com/openshwprojects/OpenDyson.git
   cd OpenDyson

   # Build the binary
   go build -o opendyson cmd/opendyson/main.go
   ```

2. **Extract your device credentials**:
   ```bash
   # List your devices and get credentials
   ./opendyson devices

   # This will output something like:
   # Device: 9HC-EU-UDB6777A
   # Username: 9HC-EU-UDB6777A
   # Password: [decrypted-password]
   # Topic Root: 438M
   ```

3. **Use the credentials in your `.env` file**:
   ```bash
   DEVICE_IP=192.168.3.82
   MQTT_PORT=1883
   MQTT_PASSWORD=[password-from-opendyson]
   ROOT_TOPIC=[topic-root-from-opendyson]
   SERIAL_NUMBER=[serial-number-from-opendyson]
   ```

### Alternative: Use the Included OpenDyson

This repository includes OpenDyson as a submodule. You can use it directly:

```bash
# Initialize and update the submodule
git submodule update --init --recursive

# Use the included OpenDyson binary
./opendyson/opendyson devices
```

## ✨ Features

- **🎛️ Device Control**: Power, fan speed, auto mode, night mode, sleep timer, oscillation, direction
- **📊 State Monitoring**: Real-time listening, on-demand state fetching
- **🤖 JSON Output**: Machine-readable responses for automation
- **🔧 Professional CLI**: Easy-to-use command-line interface

## 📖 Documentation

- **[App Documentation](./dyson2mqtt/README.md)**: Detailed usage guide, commands, and examples
- **[Game Plan](./dyson2mqtt/GAMEPLAN.md)**: Development roadmap and architecture notes
- **[Message Analysis](./dyson2mqtt/commands/dyson_message_analysis.md)**: Complete MQTT message reference

## 🏗️ Project Structure

```
dyson2mqtt/
├── dyson2mqtt/            # Main application
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
| `power` | **Control** | `dyson2mqtt power <state>` | `on\|off` | Turn the fan ON or OFF |
| `auto` | **Control** | `dyson2mqtt auto <state>` | `on\|off` | Enable/disable auto mode |
| `night` | **Control** | `dyson2mqtt night <state>` | `on\|off` | Enable/disable night mode |
| `speed` | **Control** | `dyson2mqtt speed <speed>` | `0-10` | Set fan speed (0 turns off) |
| `timer` | **Control** | `dyson2mqtt timer <time>` | `0-540`, `2h15m`, `2:15`, `1h`, `45m` | Set sleep timer (0=off) |
| `listen` | **Monitoring** | `dyson2mqtt listen` | *(none)* | Real-time monitoring (Ctrl+C to exit) |
| `state` | **Monitoring** | `dyson2mqtt state [--json]` | `--json` (optional) | Fetch current state with optional JSON output |
| `width` | **Oscillation** | `dyson2mqtt width <width>` | `off\|narrow\|medium\|wide\|full` | Set oscillation width |
| `direction` | **Oscillation** | `dyson2mqtt direction <degrees>` | `0-359` | Set oscillation direction |
| `stop` | **Oscillation** | `dyson2mqtt stop` | *(none)* | Stop oscillation |

### Command Categories

- **🎛️ Control Commands**: Direct device control (power, settings, timers)
- **📊 Monitoring Commands**: State monitoring and real-time updates
- **🔄 Oscillation Commands**: Control fan oscillation and direction

### Quick Examples

```bash
# Basic control
dyson2mqtt power on                    # Turn fan on
dyson2mqtt speed 5                     # Set speed to 5
dyson2mqtt auto on                     # Enable auto mode
dyson2mqtt night on                    # Enable night mode
dyson2mqtt timer 2h15m                 # Set 2h15m sleep timer

# Oscillation control
dyson2mqtt width wide                  # Set wide oscillation
dyson2mqtt direction 180               # Point oscillation at 180°
dyson2mqtt stop                        # Stop oscillation

# Monitoring
dyson2mqtt listen                      # Real-time status updates
dyson2mqtt state --json                # Get current state as JSON

# Automation
dyson2mqtt power on --json             # JSON output for scripts
STATUS=$(dyson2mqtt state --json)      # Capture state in variable
```

## 🤖 Automation Examples

### Shell Scripting
```bash
# Morning routine
dyson2mqtt power on
dyson2mqtt auto on
dyson2mqtt speed 3

# Get current status
STATUS=$(dyson2mqtt state --json)
echo $STATUS | jq '.state.product-state.fpwr'
```

### Python Integration
```python
import json, subprocess

result = subprocess.run(['dyson2mqtt', 'state', '--json'],
                       capture_output=True, text=True)
state = json.loads(result.stdout)

if state['success']:
    print(f"Power: {state['state']['product-state']['fpwr']}")
```

## 🔍 Troubleshooting

- **Connection issues**: Verify `.env` configuration and network connectivity
- **No response**: Use `dyson2mqtt listen` to check device communication
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
git clone https://github.com/RoyalPineapple/dyson2mqtt.git
cd dyson2mqtt

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

- **[App Documentation](./dyson2mqtt/README.md)** - Detailed usage, architecture, and examples
- **[Message Analysis](./dyson2mqtt/commands/dyson_message_analysis.md)** - Complete MQTT message reference
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines and setup
- **[Changelog](CHANGELOG.md)** - Version history and changes
