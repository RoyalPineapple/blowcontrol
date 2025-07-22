"""
Night mode command module for Dyson2MQTT app.
"""
import logging
from typing import Union
from dyson2mqtt.mqtt.client import DysonMQTTClient
from dyson2mqtt.utils import parse_boolean

logger = logging.getLogger(__name__)

def set_night_mode(on: Union[bool, str, int]) -> bool:
    """
    Set the Dyson device night mode ON or OFF via MQTT.
    
    Args:
        on: Boolean value or string representation. Supports:
            - True/False, "true"/"false", "t"/"f"
            - "1"/"0", "on"/"off", "yes"/"no", "y"/"n"
    
    Returns True if successful, False otherwise.
    """
    try:
        # Parse flexible boolean input
        night_on = parse_boolean(on)
        
        client = DysonMQTTClient(client_id="d2mqtt-cmd")
        client.connect()
        client.set_boolean_state('nmod', night_on)
        client.disconnect()
        return True
    except Exception as e:
        logger.error(f"Failed to set night mode: {e}")
        return False 