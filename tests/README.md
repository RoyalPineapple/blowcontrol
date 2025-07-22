# Dyson2MQTT Test Suite

A comprehensive test suite for the Dyson2MQTT project, covering unit tests, integration tests, and mock tests.

## 🚀 Quick Start

### Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
# Using the test runner
python tests/run_tests.py

# Or directly with pytest
pytest tests/
```

### Run Specific Test Types
```bash
# Unit tests only
python tests/run_tests.py --type unit

# Integration tests only
python tests/run_tests.py --type integration

# With coverage report
python tests/run_tests.py --coverage

# Verbose output
python tests/run_tests.py --verbose
```

## 📁 Test Structure

```
tests/
├── __init__.py              # Test package
├── conftest.py             # Pytest configuration and fixtures
├── run_tests.py            # Test runner script
├── README.md               # This file
├── unit/                   # Unit tests
│   ├── __init__.py
│   ├── test_config.py      # Configuration tests
│   ├── test_mqtt_client.py # MQTT client tests
│   └── test_commands.py    # Command module tests
├── integration/            # Integration tests
│   ├── __init__.py
│   └── test_cli.py         # CLI interface tests
└── mocks/                  # Mock tests
    └── __init__.py
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
- **Configuration Management**: Environment variables, .env loading, validation
- **MQTT Client**: Connection, publishing, subscribing, state management
- **Commands**: Power, fan speed, auto mode, night mode, sleep timer
- **State Management**: Device state parsing and formatting

### Integration Tests (`tests/integration/`)
- **CLI Interface**: Command-line argument parsing, output formatting
- **End-to-End**: Full command execution with mocked dependencies
- **JSON Output**: Machine-readable response validation

### Mock Tests (`tests/mocks/`)
- **External Dependencies**: MQTT broker, device communication
- **Network Operations**: Connection handling, timeout scenarios
- **Error Conditions**: Network failures, invalid responses

## 🔧 Test Fixtures

The test suite includes comprehensive fixtures in `conftest.py`:

- **`mock_env_vars`**: Mock environment variables for testing
- **`mock_mqtt_client`**: Mock MQTT client with all methods
- **`sample_device_state`**: Sample device state data
- **`sample_environmental_data`**: Sample environmental sensor data
- **`temp_env_file`**: Temporary .env file for testing
- **`mock_mqtt_message`**: Mock MQTT message
- **`mock_logger`**: Mock logger for testing

## 📊 Coverage

Generate coverage reports:
```bash
# Terminal coverage report
pytest --cov=dyson2mqtt --cov-report=term-missing

# HTML coverage report
pytest --cov=dyson2mqtt --cov-report=html

# Both
pytest --cov=dyson2mqtt --cov-report=term-missing --cov-report=html
```

## 🎯 Test Examples

### Running Specific Tests
```bash
# Run only configuration tests
pytest tests/unit/test_config.py

# Run only MQTT client tests
pytest tests/unit/test_mqtt_client.py

# Run tests matching a pattern
pytest -k "power" tests/

# Run tests with specific markers
pytest -m "slow" tests/
```

### Debugging Tests
```bash
# Run with maximum verbosity
pytest -vvv tests/

# Stop on first failure
pytest -x tests/

# Show local variables on failure
pytest -l tests/

# Run with debugger on failure
pytest --pdb tests/
```

## 🔍 Test Patterns

### Mocking External Dependencies
```python
@patch('dyson2mqtt.mqtt.client.DysonMQTTClient')
def test_mqtt_operation(self, mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Test your code here
    result = some_function()
    
    # Verify mocks were called correctly
    mock_client.connect.assert_called_once()
```

### Testing Error Conditions
```python
def test_error_handling(self):
    with patch('some_module.some_function', side_effect=Exception("Test error")):
        result = function_under_test()
        assert result is False  # Should handle error gracefully
```

### Testing CLI Commands
```python
def test_cli_command(self):
    result = subprocess.run([
        sys.executable, '-m', 'dyson2mqtt', 'power', 'on'
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert '✓' in result.stdout
```

## 🚨 Common Issues

### Import Errors
If you get import errors, make sure:
1. You're running tests from the project root
2. The `dyson2mqtt` module is in your Python path
3. All dependencies are installed

### Mock Issues
If mocks aren't working:
1. Check that you're patching the correct import path
2. Ensure mocks are applied before the module is imported
3. Use `patch.object()` for instance methods

### Test Isolation
For proper test isolation:
1. Use fixtures to set up test data
2. Clean up any temporary files
3. Reset mocks between tests

## 📈 Continuous Integration

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    pytest tests/ --cov=dyson2mqtt --cov-report=xml
```

## 🤝 Contributing

When adding new tests:

1. **Follow the existing structure** - Put tests in appropriate directories
2. **Use descriptive names** - Test names should explain what they test
3. **Add docstrings** - Explain what each test validates
4. **Use fixtures** - Reuse existing fixtures or create new ones
5. **Test edge cases** - Include error conditions and boundary values
6. **Keep tests fast** - Avoid slow operations, use mocks for external calls

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html) 