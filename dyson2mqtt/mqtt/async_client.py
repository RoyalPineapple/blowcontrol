"""
Async MQTT client for Dyson2MQTT modular app.

Uses asyncio with existing paho-mqtt (no additional dependencies).
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
import threading
import time
from dyson2mqtt.mqtt.client import DysonMQTTClient
from dyson2mqtt.state.device_state import DeviceStatePrinter
from dyson2mqtt.config import ROOT_TOPIC, SERIAL_NUMBER

logger = logging.getLogger(__name__)


async def async_get_state(timeout: float = 60, quiet: bool = False) -> Optional[Dict[str, Any]]:
    """
    Async function to get current device state using existing sync client.
    Uses asyncio.to_thread to run sync code in a thread pool.
    """
    if not ROOT_TOPIC or not SERIAL_NUMBER:
        raise ValueError("ROOT_TOPIC and SERIAL_NUMBER must be set.")
    
    def sync_get_state():
        """Sync function to get state - runs in thread pool."""
        topics = [
            f"{ROOT_TOPIC}/{SERIAL_NUMBER}/status/current",
            f"{ROOT_TOPIC}/{SERIAL_NUMBER}/status/fault"
        ]
        
        client = DysonMQTTClient(client_id="d2mqtt-async-getstate")
        result = {"state": None, "environmental": None}
        got_response = threading.Event()
        
        def state_callback(client_, userdata, msg):
            try:
                data = json.loads(msg.payload.decode(errors='replace'))
                msg_type = data.get("msg")
                
                if msg_type == "CURRENT-STATE":
                    if not quiet:
                        print("[ASYNC] ✓ Received device state")
                    result["state"] = data
                    got_response.set()
                elif msg_type == "ENVIRONMENTAL-CURRENT-SENSOR-DATA":
                    if not quiet:
                        print("[ASYNC] ✓ Received environmental data")
                    result["environmental"] = data
                elif msg_type == "STATE-CHANGE":
                    if not result["state"]:
                        if not quiet:
                            print("[ASYNC] ✓ Received state change")
                        result["state"] = data
                        got_response.set()
                    
            except Exception as e:
                if not quiet:
                    print(f"[ASYNC] ⚠ Parse error: {e}")
        
        try:
            # Replicate the exact subscribe_and_listen pattern
            if not quiet:
                print("[ASYNC] Connecting to device...")
            else:
                # Suppress INFO logs when in quiet mode
                import logging
                logging.getLogger('app.mqtt.client').setLevel(logging.WARNING)
            
            client._subscribed_topics = topics
            client._user_callback = state_callback
            client._client.on_message = state_callback
            
            client.connect()
            
            if not quiet:
                print("[ASYNC] Waiting for connection...")
            import time
            time.sleep(2)  # Give time for connection and subscription to complete
            
            if not quiet:
                print("[ASYNC] Requesting device state...")
            client.send_command("REQUEST-CURRENT-STATE")
            
            if got_response.wait(timeout=timeout):
                if not quiet:
                    print("[ASYNC] ✓ State received successfully")
                return result
            else:
                if not quiet:
                    print("[ASYNC] ⚠ Timeout - no response from device")
                return result
                
        except Exception as e:
            if not quiet:
                print(f"[ASYNC] ✗ Error: {e}")
            return result
        finally:
            try:
                client.disconnect()
            except:
                pass
    
    # Run sync function in thread pool
    return await asyncio.to_thread(sync_get_state)


async def async_send_command(command: str) -> bool:
    """
    Async function to send a command using existing sync client.
    """
    def sync_send_command():
        """Sync function to send command - runs in thread pool."""
        try:
            client = DysonMQTTClient(client_id="d2mqtt-async-cmd")
            client.connect()
            client.send_command(command)
            client.disconnect()
            return True
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
    
    # Run sync function in thread pool
    return await asyncio.to_thread(sync_send_command)


async def async_set_power(on: bool) -> bool:
    """Async function to set power state."""
    def sync_set_power():
        try:
            client = DysonMQTTClient(client_id="d2mqtt-async-cmd")
            client.connect()
            client.set_boolean_state('fpwr', on)
            client.disconnect()
            return True
        except Exception as e:
            logger.error(f"Error setting power: {e}")
            return False
    
    return await asyncio.to_thread(sync_set_power)


async def async_set_fan_speed(speed: int) -> bool:
    """Async function to set fan speed."""
    def sync_set_fan_speed():
        try:
            if speed == 0:
                # Power off
                client = DysonMQTTClient(client_id="d2mqtt-async-cmd")
                client.connect()
                client.set_boolean_state('fpwr', False)
                client.disconnect()
            else:
                client = DysonMQTTClient(client_id="d2mqtt-async-cmd")
                client.connect()
                speed_str = f"{speed:04d}"
                client.set_numeric_state('fnsp', speed_str)
                client.disconnect()
            return True
        except Exception as e:
            logger.error(f"Error setting fan speed: {e}")
            return False
    
    return await asyncio.to_thread(sync_set_fan_speed) 