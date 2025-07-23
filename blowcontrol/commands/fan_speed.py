"""
Fan speed command module for Dyson2MQTT app.
"""

import logging
from typing import Any, Union

from blowcontrol.commands.power import set_power
from blowcontrol.mqtt.client import DysonMQTTClient

logger = logging.getLogger(__name__)


def parse_int_input(value: Any) -> int:
    """
    Parse integer input from string or int.
    Raises ValueError for invalid input.
    """
    if isinstance(value, str):
        return int(value)
    elif isinstance(value, int):
        return value
    else:
        raise ValueError(f"Cannot convert {value} to integer")


def validate_fan_speed(speed: Union[int, str, Any]) -> int:
    """
    Validate and normalize fan speed. Returns int if valid, raises ValueError if not.
    """
    speed_int = parse_int_input(speed)
    if not (0 <= speed_int <= 10):
        raise ValueError("Fan speed must be between 0 and 10.")
    return speed_int


def set_fan_speed(speed: Union[int, str]) -> bool:
    """
    Set the Dyson device fan speed (0-10) via MQTT.

    Args:
        speed: Fan speed as integer or string (0-10). 0 will power off the fan.

    Returns True if successful, False otherwise.
    """
    try:
        validated_speed = validate_fan_speed(speed)
        if validated_speed == 0:
            # Speed 0 means turn off the fan
            return set_power(False)

        client = DysonMQTTClient(client_id="d2mqtt-cmd")
        client.connect()
        speed_str = f"{validated_speed:04d}"
        client.set_numeric_state("fnsp", speed_str)
        client.disconnect()
        return True
    except Exception as e:
        logger.error(f"Failed to set fan speed: {e}")
        return False
