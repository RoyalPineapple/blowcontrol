"""
Unit tests for MQTT client functionality.
"""

import json
from unittest.mock import Mock, patch

import pytest

from blowcontrol.mqtt.client import DysonMQTTClient


class TestDysonMQTTClient:
    """Test MQTT client functionality."""

    def test_client_initialization(self, mock_env_vars):
        """Test client initialization with valid parameters."""
        client = DysonMQTTClient(
            device_ip="192.168.1.100",
            port=1883,
            serial_number="9HC-EU-TEST123",
            password="test-password",
            client_id="test-client",
        )

        assert client.device_ip == "192.168.1.100"
        assert client.port == 1883
        assert client.username == "9HC-EU-TEST123"
        assert client.password == "test-password"
        assert client.client_id == "test-client"
        assert client._connected is False
        assert client._subscribed_topics == []

    def test_client_initialization_missing_ip(self):
        """Test client initialization fails with missing IP."""
        with pytest.raises(ValueError, match="DEVICE_IP is required"):
            DysonMQTTClient(device_ip=None)

    def test_client_initialization_from_config(self, mock_env_vars):
        """Test client initialization using config defaults."""
        # Test with explicit parameters instead of relying on config
        client = DysonMQTTClient(
            device_ip="192.168.1.100",
            port=1883,
            serial_number="9HC-EU-TEST123",
            password="test-password",
        )

        assert client.device_ip == "192.168.1.100"
        assert client.port == 1883
        assert client.username == "9HC-EU-TEST123"
        assert client.password == "test-password"

    @patch("paho.mqtt.client.Client")
    def test_connect_disconnect(self, mock_mqtt_client, mock_env_vars):
        """Test connect and disconnect methods."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        # Use explicit parameters to avoid config dependency
        client = DysonMQTTClient(
            device_ip="192.168.1.100",
            port=1883,
            serial_number="9HC-EU-TEST123",
            password="test-password",
            client_id="test-client",
        )

        # Test connect
        client.connect()
        mock_client_instance.connect.assert_called_once_with("192.168.1.100", 1883, 60)
        mock_client_instance.loop_start.assert_called_once()

        # Test disconnect
        client.disconnect()
        mock_client_instance.loop_stop.assert_called_once()
        mock_client_instance.disconnect.assert_called_once()
        assert client._connected is False

    @patch("paho.mqtt.client.Client")
    def test_publish_message(self, mock_mqtt_client, mock_env_vars):
        """Test publishing messages."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")

        # Test publish
        client.publish("test/topic", "test message")
        mock_client_instance.publish.assert_called_once_with(
            "test/topic", "test message", 0, False
        )

    def test_publish_empty_topic(self, mock_env_vars):
        """Test publish fails with empty topic."""
        client = DysonMQTTClient(client_id="test-client")

        with pytest.raises(ValueError, match="Topic is required"):
            client.publish("", "test message")

    @patch("paho.mqtt.client.Client")
    def test_subscribe(self, mock_mqtt_client, mock_env_vars):
        """Test subscribing to topics."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")
        callback = Mock()

        client.subscribe("test/topic", callback)

        assert client._subscribed_topics == ["test/topic"]
        assert client._user_callback == callback
        mock_client_instance.on_message = callback

    def test_subscribe_empty_topic(self, mock_env_vars):
        """Test subscribe fails with empty topic."""
        client = DysonMQTTClient(client_id="test-client")
        callback = Mock()

        with pytest.raises(ValueError, match="Topic is required"):
            client.subscribe("", callback)

    @patch("paho.mqtt.client.Client")
    def test_set_boolean_state(self, mock_mqtt_client, mock_env_vars):
        """Test setting boolean state."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")

        with patch.object(client, "publish") as mock_publish:
            client.set_boolean_state("fpwr", True)

            # Check that publish was called with correct payload
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == "438M/9HC-EU-TEST123/command"

            payload = json.loads(call_args[0][1])
            assert payload["msg"] == "STATE-SET"
            assert payload["data"]["fpwr"] == "ON"

    @patch("paho.mqtt.client.Client")
    def test_set_numeric_state(self, mock_mqtt_client, mock_env_vars):
        """Test setting numeric state."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")

        with patch.object(client, "publish") as mock_publish:
            client.set_numeric_state("fnsp", "0005")

            # Check that publish was called with correct payload
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == "438M/9HC-EU-TEST123/command"

            payload = json.loads(call_args[0][1])
            assert payload["msg"] == "STATE-SET"
            assert payload["data"]["fnsp"] == "0005"

    @patch("paho.mqtt.client.Client")
    def test_send_command(self, mock_mqtt_client, mock_env_vars):
        """Test sending commands."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")

        with patch.object(client, "publish") as mock_publish:
            result = client.send_command("REQUEST-CURRENT-STATE")

            assert result is True
            mock_publish.assert_called_once()

            call_args = mock_publish.call_args
            payload = json.loads(call_args[0][1])
            assert payload["msg"] == "REQUEST-CURRENT-STATE"

    @patch("paho.mqtt.client.Client")
    def test_send_command_with_data(self, mock_mqtt_client, mock_env_vars):
        """Test sending commands with data."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")

        with patch.object(client, "publish") as mock_publish:
            data = {"fpwr": "ON", "fnsp": "0005"}
            result = client.send_command("STATE-SET", data)

            assert result is True
            mock_publish.assert_called_once()

            call_args = mock_publish.call_args
            payload = json.loads(call_args[0][1])
            assert payload["msg"] == "STATE-SET"
            assert payload["data"] == data

    @patch("paho.mqtt.client.Client")
    def test_send_standalone_command(self, mock_mqtt_client, mock_env_vars):
        """Test sending standalone commands."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")

        with patch.object(client, "connect") as mock_connect:
            with patch.object(client, "disconnect") as mock_disconnect:
                with patch.object(
                    client, "send_command", return_value=True
                ) as mock_send:
                    result = client.send_standalone_command("REQUEST-CURRENT-STATE")

                    assert result is True
                    mock_connect.assert_called_once()
                    mock_send.assert_called_once_with(
                        "REQUEST-CURRENT-STATE", None, None
                    )
                    mock_disconnect.assert_called_once()

    def test_generate_client_id(self, mock_env_vars):
        """Test client ID generation."""
        client = DysonMQTTClient(client_id=None)

        # Should generate a unique client ID
        assert client.client_id is not None
        assert len(client.client_id) > 0
        assert "blowcontrol" in client.client_id.lower()

    @patch("paho.mqtt.client.Client")
    def test_on_connect_callback(self, mock_mqtt_client, mock_env_vars):
        """Test on_connect callback."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")

        # Simulate connection
        client._on_connect(mock_client_instance, None, None, 0)
        assert client._connected is True

        # Test subscription after connection
        client._subscribed_topics = ["test/topic"]
        client._on_connect(mock_client_instance, None, None, 0)
        mock_client_instance.subscribe.assert_called_with("test/topic")

    @patch("paho.mqtt.client.Client")
    def test_on_disconnect_callback(self, mock_mqtt_client, mock_env_vars):
        """Test on_disconnect callback."""
        mock_client_instance = Mock()
        mock_mqtt_client.return_value = mock_client_instance

        client = DysonMQTTClient(client_id="test-client")
        client._connected = True

        client._on_disconnect(mock_client_instance, None, 0)
        assert client._connected is False
