"""
Power command module for Dyson2MQTT app.
"""

import logging
from typing import Union

from blowcontrol.mqtt.client import DysonMQTTClient
from blowcontrol.utils import parse_boolean

logger = logging.getLogger(__name__)


def set_power(on: Union[bool, str, int]) -> bool:
    """
    Set the Dyson device power ON or OFF via MQTT.

    Args:
        on: Boolean value or string representation. Supports:
            - True/False, "true"/"false", "t"/"f"
            - "1"/"0", "on"/"off", "yes"/"no", "y"/"n"

    Returns True if successful, False otherwise.
    """
    try:
        # Parse flexible boolean input
        power_on = parse_boolean(on)

        client = DysonMQTTClient(client_id="d2mqtt-cmd")
        client.connect()
        client.set_boolean_state("fpwr", power_on)
        client.disconnect()
        return True
    except Exception as e:
        logger.error(f"Failed to set power: {e}")
        return False


def request_current_state() -> None:
    """
    Send a REQUEST-CURRENT-STATE command to the Dyson device.
    """
    client = DysonMQTTClient(client_id="d2mqtt-cmd")
    client.connect()
    client.send_command("REQUEST-CURRENT-STATE")
    client.disconnect()
