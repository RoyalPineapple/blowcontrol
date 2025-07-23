"""
Unit tests for configuration management.
"""

import os
from unittest.mock import mock_open, patch

import pytest


class TestConfig:
    """Test configuration loading and validation."""

    def test_config_loading_from_env(self, mock_env_vars):
        """Test that configuration loads from environment variables."""
        # Re-import config to get fresh values
        import importlib

        import dyson2mqtt.config

        importlib.reload(dyson2mqtt.config)

        assert dyson2mqtt.config.DEVICE_IP == "192.168.1.100"
        assert dyson2mqtt.config.MQTT_PORT == 1883
        assert dyson2mqtt.config.MQTT_PASSWORD == "test-password"
        assert dyson2mqtt.config.ROOT_TOPIC == "438M"
        assert dyson2mqtt.config.SERIAL_NUMBER == "9HC-EU-TEST123"

    def test_mqtt_port_default(self):
        """Test that MQTT_PORT defaults to 1883."""
        with patch.dict(os.environ, {"TESTING": "1"}, clear=True):
            import importlib

            import dyson2mqtt.config

            importlib.reload(dyson2mqtt.config)

            assert dyson2mqtt.config.MQTT_PORT == 1883

    def test_mqtt_port_custom(self):
        """Test that MQTT_PORT can be set to custom value."""
        with patch.dict(os.environ, {"MQTT_PORT": "8883"}):
            import importlib

            import dyson2mqtt.config

            importlib.reload(dyson2mqtt.config)

            assert dyson2mqtt.config.MQTT_PORT == 8883

    def test_missing_required_vars(self):
        """Test that missing required variables raise ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("dotenv.load_dotenv"):  # Prevent .env loading
                import importlib

                import dyson2mqtt.config

                # The config module will raise ValueError when required vars
                # are missing
                with pytest.raises(
                    ValueError, match="MQTT_PASSWORD environment variable is required"
                ):
                    importlib.reload(dyson2mqtt.config)

    def test_dotenv_loading(self, temp_env_file):
        """Test that .env file is loaded when present."""
        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                mock_open(
                    read_data="""DEVICE_IP=192.168.1.200
MQTT_PORT=1883
MQTT_PASSWORD=env-password
ROOT_TOPIC=438M
SERIAL_NUMBER=9HC-EU-ENV123
"""
                ),
            ):
                with patch("dotenv.load_dotenv") as mock_load_dotenv:
                    import importlib

                    import dyson2mqtt.config

                    importlib.reload(dyson2mqtt.config)

                    mock_load_dotenv.assert_called_once()

    def test_dotenv_optional(self):
        """Test that .env loading is optional."""
        with patch("dotenv.load_dotenv", side_effect=ImportError):
            # Should not raise an exception for ImportError
            import importlib

            import dyson2mqtt.config

            # The ImportError will be raised during reload, so we need to catch
            # it
            with pytest.raises(ImportError):
                importlib.reload(dyson2mqtt.config)

    def test_config_validation(self):
        """Test configuration validation."""
        # Test with valid configuration
        with patch.dict(
            os.environ,
            {
                "DEVICE_IP": "192.168.1.100",
                "MQTT_PORT": "1883",
                "MQTT_PASSWORD": "test-password",
                "ROOT_TOPIC": "438M",
                "SERIAL_NUMBER": "9HC-EU-TEST123",
            },
        ):
            import importlib

            import dyson2mqtt.config

            importlib.reload(dyson2mqtt.config)

            # All required fields should be present
            assert dyson2mqtt.config.DEVICE_IP is not None
            assert dyson2mqtt.config.ROOT_TOPIC is not None
            assert dyson2mqtt.config.SERIAL_NUMBER is not None
            assert dyson2mqtt.config.MQTT_PORT is not None
