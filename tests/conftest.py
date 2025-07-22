"""
Pytest configuration and fixtures for Dyson2MQTT test suite.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
import json

# Add the project root to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))





@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    test_env = {
        'DEVICE_IP': '192.168.1.100',
        'MQTT_PORT': '1883',
        'MQTT_PASSWORD': 'test-password',
        'ROOT_TOPIC': '438M',
        'SERIAL_NUMBER': '9HC-EU-TEST123'
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_mqtt_client():
    """Mock MQTT client for testing."""
    mock_client = Mock()
    mock_client.device_ip = '192.168.1.100'
    mock_client.port = 1883
    mock_client.username = '9HC-EU-TEST123'
    mock_client.password = 'test-password'
    mock_client.client_id = 'test-client'
    mock_client._connected = False
    mock_client._subscribed_topics = []
    
    # Mock methods
    mock_client.connect.return_value = None
    mock_client.disconnect.return_value = None
    mock_client.publish.return_value = None
    mock_client.subscribe.return_value = None
    mock_client.send_command.return_value = True
    mock_client.send_standalone_command.return_value = True
    mock_client.set_boolean_state.return_value = None
    mock_client.set_numeric_state.return_value = None
    
    return mock_client


@pytest.fixture
def sample_device_state():
    """Sample device state for testing."""
    return {
        "msg": "CURRENT-STATE",
        "time": "2025-07-22T21:41:44.000Z",
        "product-state": {
            "fpwr": "ON",
            "fnsp": "0002",
            "auto": "OFF",
            "nmod": "OFF",
            "oson": "OFF",
            "oscs": "OFF",
            "osal": "0090",
            "osau": "0090",
            "ancp": "CUST",
            "sltm": "OFF",
            "rhtm": "ON",
            "cflr": "INV",
            "hflr": "0100",
            "cflt": "NONE",
            "hflt": "GCOM"
        }
    }


@pytest.fixture
def sample_environmental_data():
    """Sample environmental data for testing."""
    return {
        "msg": "ENVIRONMENTAL-CURRENT-SENSOR-DATA",
        "time": "2025-07-22T21:41:44.000Z",
        "data": {
            "pm25": "0091",
            "pm10": "0072",
            "pm25_avg": "0078",
            "pm10_avg": "0079"
        }
    }


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("""# Test environment
DEVICE_IP=192.168.1.100
MQTT_PORT=1883
MQTT_PASSWORD=test-password
ROOT_TOPIC=438M
SERIAL_NUMBER=9HC-EU-TEST123
""")
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except OSError:
        pass


@pytest.fixture
def mock_mqtt_message():
    """Mock MQTT message for testing."""
    message = Mock()
    message.topic = "438M/9HC-EU-TEST123/status/current"
    message.payload = json.dumps({
        "msg": "CURRENT-STATE",
        "time": "2025-07-22T21:41:44.000Z",
        "product-state": {
            "fpwr": "ON",
            "fnsp": "0002"
        }
    }).encode('utf-8')
    return message


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger 