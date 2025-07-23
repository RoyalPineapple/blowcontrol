"""
Configuration management for Dyson2MQTT.
Loads settings from environment variables and .env file.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Device configuration
DEVICE_IP = os.getenv("DEVICE_IP", "192.168.1.100")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
ROOT_TOPIC = os.getenv("ROOT_TOPIC", "438M")
SERIAL_NUMBER = os.getenv("SERIAL_NUMBER", "")


def validate_config():
    """Validate required configuration settings."""
    if not MQTT_PASSWORD:
        raise ValueError("MQTT_PASSWORD environment variable is required")
    if not SERIAL_NUMBER:
        raise ValueError("SERIAL_NUMBER environment variable is required")


# Only validate if not in test environment
if not os.getenv("TESTING"):
    validate_config()

# MQTT topic construction


def get_device_topic(suffix: str = "") -> str:
    """Construct MQTT topic for device communication."""
    base_topic = f"{ROOT_TOPIC}/{SERIAL_NUMBER}"
    return f"{base_topic}/{suffix}" if suffix else base_topic


# Status topics
STATUS_CURRENT_TOPIC = get_device_topic("status/current")
STATUS_FAULT_TOPIC = get_device_topic("status/fault")
COMMAND_TOPIC = get_device_topic("command")
