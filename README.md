# Dyson2MQTT

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/RoyalPineapple/dyson2mqtt/workflows/Tests%20and%20Code%20Quality/badge.svg)](https://github.com/RoyalPineapple/dyson2mqtt/actions)
[![Codecov](https://codecov.io/gh/RoyalPineapple/dyson2mqtt/branch/master/graph/badge.svg)](https://codecov.io/gh/RoyalPineapple/dyson2mqtt)

A modular Python application for controlling Dyson fans via MQTT with support for real-time monitoring, async operations, and machine-readable JSON output.

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install paho-mqtt python-dotenv
   ```

2. **Configure your device** (create `.env` file):
   ```bash
   DEVICE_IP=192.168.3.82
   MQTT_PORT=1883
   MQTT_PASSWORD=your-mqtt-password
   ROOT_TOPIC=438M
   SERIAL_NUMBER=9HC-EU-UDB6777A
   ```

3. **Control your device**:
   ```bash
   # Basic control
   python3 -m app power on
   python3 -m app speed 5
   
   # Monitor state
   python3 -m app listen
   
   # Get JSON output for automation
   python3 -m app state --json
   ```

## ✨ Features

- **🎛️ Device Control**: Power, fan speed, auto mode, night mode, sleep timer
- **📊 State Monitoring**: Real-time listening, on-demand state fetching  
- **⚡ Async Support**: Non-blocking operations with async/await
- **🤖 JSON Output**: Machine-readable responses for automation
- **🔧 Thread-Safe**: Background listeners with proper synchronization
- **🎨 Clean CLI**: Professional interface with helpful output

## 📖 Documentation

- **[App Documentation](./app/README.md)**: Detailed usage guide, commands, and examples
- **[Game Plan](./app/GAMEPLAN.md)**: Development roadmap and architecture notes
- **[Experimentation](./experimentation/README.md)**: Research and message analysis

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
| `power` | **Control** | `python3 -m app power <state>` | `on\|off` | Turn the fan ON or OFF |
| `auto` | **Control** | `python3 -m app auto <state>` | `on\|off` | Enable/disable auto mode |
| `night` | **Control** | `python3 -m app night <state>` | `on\|off` | Enable/disable night mode |
| `speed` | **Control** | `python3 -m app speed <speed>` | `0-10` | Set fan speed (0 turns off) |
| `timer` | **Control** | `python3 -m app timer <time>` | `0-540`, `2h15m`, `2:15`, `1h`, `45m` | Set sleep timer (0=off) |
| `listen` | **Monitoring** | `python3 -m app listen` | *(none)* | Real-time monitoring (Ctrl+C to exit) |
| `state` | **Monitoring** | `python3 -m app state [--json]` | `--json` (optional) | Fetch current state with optional JSON output |

### Command Categories

- **🎛️ Control Commands**: Direct device control (power, settings, timers)
- **📊 Monitoring Commands**: State monitoring and real-time updates

### Quick Examples

### Shell Scripting
```bash
# Morning routine
python3 -m app power on
python3 -m app auto on
python3 -m app speed 3

# Get current status
STATUS=$(python3 -m app state --json)
echo $STATUS | jq '.state.product-state.fpwr'
```

### Python Integration
```python
import json, subprocess

result = subprocess.run(['python3', '-m', 'app', 'state', '--json'], 
                       capture_output=True, text=True)
state = json.loads(result.stdout)

if state['success']:
    print(f"Power: {state['state']['product-state']['fpwr']}")
```

## 🤖 Automation Examples

### Shell Scripting
```bash
# Morning routine
python3 -m app power on
python3 -m app auto on
python3 -m app speed 3

# Get current status
STATUS=$(python3 -m app state --json)
echo $STATUS | jq '.state.product-state.fpwr'
```

### Python Integration
```python
import json, subprocess

result = subprocess.run(['python3', '-m', 'app', 'state', '--json'], 
                       capture_output=True, text=True)
state = json.loads(result.stdout)

if state['success']:
    print(f"Power: {state['state']['product-state']['fpwr']}")
```

## 🔍 Troubleshooting

- **Connection issues**: Verify `.env` configuration and network connectivity
- **No response**: Use `python3 -m app listen` to check device communication  
- **JSON parsing**: Ensure you're using `--json` flag for machine-readable output

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
black dyson2mqtt/ tests/
isort dyson2mqtt/ tests/
flake8 dyson2mqtt/ tests/
mypy dyson2mqtt/
```

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

**Ready to control your Dyson device like a pro!** 🌪️

## 📚 Documentation

- **[App Documentation](./app/README.md)** - Detailed usage, architecture, and examples
- **[Message Analysis](./experimentation/dyson_message_analysis.md)** - Complete MQTT message reference  
- **[Development Roadmap](./app/GAMEPLAN.md)** - Project roadmap and checklist
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines and setup
- **[Changelog](CHANGELOG.md)** - Version history and changes 
