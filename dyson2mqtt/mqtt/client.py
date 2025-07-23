"""
MQTT client for Dyson2MQTT modular app.

Requires paho-mqtt:
    pip install paho-mqtt
"""

import datetime
import logging
import random
import string
from typing import Any, Callable, Optional, Union

import paho.mqtt.client as mqtt

from dyson2mqtt.config import DEVICE_IP, MQTT_PASSWORD, MQTT_PORT, SERIAL_NUMBER

logger = logging.getLogger(__name__)


class DysonMQTTClient:
    """
    Reusable MQTT client for Dyson2MQTT app.
    Uses SERIAL_NUMBER as the MQTT username.
    """

    def __init__(
        self,
        device_ip: Optional[str] = DEVICE_IP,
        port: int = MQTT_PORT,
        serial_number: Optional[str] = SERIAL_NUMBER,
        password: Optional[str] = MQTT_PASSWORD,
        client_id: Optional[str] = None,
    ):
        if not device_ip:
            raise ValueError("DEVICE_IP is required but not set.")
        self.device_ip = device_ip
        self.port = port
        self.username = serial_number
        self.password = password
        self.client_id = client_id or self._generate_client_id()
        self._client = mqtt.Client(client_id=self.client_id)
        if self.username and self.password:
            self._client.username_pw_set(self.username, self.password)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = None  # Set by user if needed
        self._connected = False
        self._subscribed_topics: list[str] = []
        self._user_callback = None

    def connect(self, keepalive: int = 60) -> None:
        """Connect to the MQTT broker."""
        logger.info(f"Connecting to MQTT broker at {self.device_ip}:{self.port}...")
        self._client.connect(self.device_ip, self.port, keepalive)
        self._client.loop_start()

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        logger.info("Disconnecting from MQTT broker...")
        self._client.loop_stop()
        self._client.disconnect()
        self._connected = False

    def publish(
        self, topic: str, payload: str, qos: int = 0, retain: bool = False
    ) -> None:
        """Publish a message to a topic."""
        if not topic:
            raise ValueError("Topic is required for publish().")
        logger.debug(f"Publishing to {topic}: {payload}")
        self._client.publish(topic, payload, qos, retain)

    def subscribe(self, topic: str, callback: Callable) -> None:
        """Subscribe to a topic and set a callback for received messages."""
        if not topic:
            raise ValueError("Topic is required for subscribe().")
        logger.info(f"Subscribing to topic: {topic}")
        self._subscribed_topics = [topic]
        self._user_callback = callback
        if self._connected:
            self._client.subscribe(topic)
        self._client.on_message = callback  # type: ignore

    def subscribe_and_listen(
        self, topics: Union[str, list[str]], callback: Optional[Callable] = None
    ) -> None:
        """
        Subscribe to one or more topics and print all received messages until interrupted.
        :param topics: str or list of str
        :param callback: Optional custom callback. If None, print topic and payload.
        """
        import signal

        if isinstance(topics, str):
            topics = [topics]

        def default_callback(client: Any, userdata: Any, msg: Any) -> None:
            print(f"[MQTT] {msg.topic}: {msg.payload.decode(errors='replace')}")

        cb = callback or default_callback
        self._subscribed_topics = topics
        self._user_callback = cb
        self._client.on_message = cb  # type: ignore
        self.connect()
        print("Listening for messages. Press Ctrl+C to exit.")
        try:
            signal.pause()
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting listener...")
            self.disconnect()

    def set_boolean_state(
        self, key: str, value: bool, topic: Optional[str] = None
    ) -> None:
        """
        Set a boolean state (ON/OFF) for the Dyson device.
        :param key: The data key to set (e.g., 'fpwr', 'auto', 'nmod', 'oson')
        :param value: True for ON, False for OFF
        :param topic: Optional override for the MQTT topic
        """
        from dyson2mqtt.config import ROOT_TOPIC, SERIAL_NUMBER

        if not topic:
            if not ROOT_TOPIC:
                raise ValueError("ROOT_TOPIC is required but not set.")
            if not SERIAL_NUMBER:
                raise ValueError("SERIAL_NUMBER is required but not set.")
            topic = f"{ROOT_TOPIC}/{SERIAL_NUMBER}/command"
        str_value = "ON" if value else "OFF"
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        payload = {
            "msg": "STATE-SET",
            "mode-reason": "RAPP",
            "time": now,
            "data": {key: str_value},
        }
        import json

        logger.info(f"Setting {key} to {str_value} on topic {topic}")
        self.publish(topic, json.dumps(payload))

    def set_numeric_state(
        self, key: str, value: str, topic: Optional[str] = None
    ) -> None:
        """
        Set a numeric or string state (e.g., fan speed) for the Dyson device.
        :param key: The data key to set (e.g., 'fnsp')
        :param value: The value to set (e.g., '0005')
        :param topic: Optional override for the MQTT topic
        """
        from dyson2mqtt.config import ROOT_TOPIC, SERIAL_NUMBER

        if not topic:
            if not ROOT_TOPIC:
                raise ValueError("ROOT_TOPIC is required but not set.")
            if not SERIAL_NUMBER:
                raise ValueError("SERIAL_NUMBER is required but not set.")
            topic = f"{ROOT_TOPIC}/{SERIAL_NUMBER}/command"
        import datetime

        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        payload = {
            "msg": "STATE-SET",
            "mode-reason": "RAPP",
            "time": now,
            "data": {key: value},
        }
        import json

        logger.info(f"Setting {key} to {value} on topic {topic}")
        self.publish(topic, json.dumps(payload))

    def send_command(
        self,
        msg_type: str,
        data: Optional[dict] = None,
        topic: Optional[str] = None,
    ) -> bool:
        """
        Send a command to the Dyson device (assumes connection is already established).
        :param msg_type: The message type (e.g., 'REQUEST-CURRENT-STATE', 'STATE-SET')
        :param data: Optional data dict for STATE-SET commands
        :param topic: Optional override for the MQTT topic
        :return: True if sent successfully, False otherwise
        """
        import datetime
        import json

        from dyson2mqtt.config import ROOT_TOPIC, SERIAL_NUMBER

        if not topic:
            if not ROOT_TOPIC or not SERIAL_NUMBER:
                raise ValueError("ROOT_TOPIC and SERIAL_NUMBER must be set.")
            topic = f"{ROOT_TOPIC}/{SERIAL_NUMBER}/command"
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        payload: dict[str, Any] = {"msg": msg_type, "mode-reason": "RAPP", "time": now}
        if data:
            payload["data"] = data

        try:
            logger.info(f"Sending {msg_type} command on topic {topic}")
            if data:
                logger.debug(f"Command data: {data}")

            self.publish(topic, json.dumps(payload))
            return True
        except Exception as e:
            logger.error(f"Failed to send {msg_type} command: {e}")
            return False

    def send_standalone_command(
        self,
        msg_type: str,
        data: Optional[dict] = None,
        topic: Optional[str] = None,
    ) -> bool:
        """
        Send a standalone command to the Dyson device (handles its own connection).
        :param msg_type: The message type (e.g., 'REQUEST-CURRENT-STATE', 'STATE-SET')
        :param data: Optional data dict for STATE-SET commands
        :param topic: Optional override for the MQTT topic
        :return: True if sent successfully, False otherwise
        """
        try:
            # Connect, send, and disconnect
            self.connect()
            result = self.send_command(msg_type, data, topic)
            self.disconnect()
            return result
        except Exception as e:
            logger.error(f"Failed to send standalone {msg_type} command: {e}")
            return False

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            logger.info("Connected to MQTT broker successfully.")
            self._connected = True
            # Subscribe to topics after (re)connect
            if self._subscribed_topics:
                for topic in self._subscribed_topics:
                    logger.info(f"(Re)subscribing to topic: {topic}")
                    self._client.subscribe(topic)
            if self._user_callback:
                self._client.on_message = self._user_callback  # type: ignore
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

    def _on_disconnect(self, client: Any, userdata: Any, rc: int) -> None:
        logger.info("Disconnected from MQTT broker.")
        self._connected = False

    def _generate_client_id(self) -> str:
        """Generate a unique client ID for MQTT connections."""
        # Generate a random string for uniqueness
        random_suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )
        return f"dyson2mqtt-{random_suffix}"
