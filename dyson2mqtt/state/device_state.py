"""
Device state pretty printer and thread-safe listener for Dyson2MQTT app.
"""

import json
import threading
import time
from typing import Any, Dict, Optional

from dyson2mqtt.config import ROOT_TOPIC, SERIAL_NUMBER
from dyson2mqtt.mqtt.client import DysonMQTTClient


class DeviceStatePrinter:
    """Enhanced printer for Dyson device state with comprehensive parameter display."""

    # Parameter descriptions for better display
    PARAM_DESCRIPTIONS = {}
    PARAM_DESCRIPTIONS.update(
        {
            # Power & Operation
            "fpwr": "Fan Power",
            "fnst": "Fan Status",
            "fnsp": "Fan Speed",
            "auto": "Auto Mode",
            # Air Quality & Modes
            "nmod": "Night Mode",
            "sltm": "Sleep Timer",
            "rhtm": "Real-time Monitoring",
            # Oscillation & Direction
            "oscs": "Oscillation Status",
            "oson": "Oscillation On",
            "osal": "Oscillation Angle Lower",
            "osau": "Oscillation Angle Upper",
            "ancp": "Angle Control Point",
            "apos": "Actual Position",
            # Display & Interface
            "bril": "Brightness",
            "wacd": "WiFi Access Code Display",
            # Device Information
            "nmdv": "Network Mode Device",
            "rssi": "WiFi Signal Strength",
            "channel": "WiFi Channel",
            # Filter Status
            "cflr": "Carbon Filter Remaining",
            "hflr": "HEPA Filter Remaining",
            "cflt": "Carbon Filter Type",
            "hflt": "HEPA Filter Type",
            "fqhp": "Filter Quality HP",
            "fghp": "Filter Grade HP",
            # Environmental sensors
            "pm25": "PM2.5 Particles",
            "pm10": "PM10 Particles",
            "p25r": "PM2.5 Running Average",
            "p10r": "PM10 Running Average",
        }
    )

    @staticmethod
    def format_value(key: str, value: str) -> str:
        """Format parameter values with units and descriptions."""
        if key in ["pm25", "pm10", "p25r", "p10r"]:
            # Convert to integer and add μg/m³ unit
            try:
                num_val = int(value)
                return f"{num_val} μg/m³"
            except (ValueError, TypeError):
                return str(value)
        elif key in ["osal", "osau", "apos"]:
            # Convert angles to degrees
            try:
                angle = int(value)
                return f"{angle}°"
            except (ValueError, TypeError):
                return str(value)
        elif key == "fnsp":
            # Format fan speed
            if value == "AUTO":
                return "AUTO"
            try:
                speed = int(value)
                return f"{speed}/10"
            except (ValueError, TypeError):
                return str(value)
        elif key == "sltm":
            # Format sleep timer
            if value == "OFF":
                return "OFF"
            try:
                minutes = int(value)
                hours = minutes // 60
                mins = minutes % 60
                if hours > 0:
                    return f"{hours}h {mins}m"
                else:
                    return f"{mins}m"
            except (ValueError, TypeError):
                return str(value)
        elif key == "hflr":
            # Format filter life as percentage
            try:
                pct = int(value)
                return f"{pct}%"
            except (ValueError, TypeError):
                return str(value)
        elif key == "rssi":
            # Format signal strength
            try:
                dbm = int(value)
                if dbm >= -30:
                    strength = "Excellent"
                elif dbm >= -40:
                    strength = "Good"
                elif dbm >= -50:
                    strength = "Fair"
                else:
                    strength = "Poor"
                return f"{dbm} dBm ({strength})"
            except (ValueError, TypeError):
                return str(value)
        else:
            return str(value)

    @staticmethod
    def print_current_state(msg: dict) -> None:
        """Print comprehensive current state with all parameters."""
        ps = msg.get("product-state", {})
        print("\n" + "=" * 50)
        print("           DYSON DEVICE STATE")
        print("=" * 50)

        # Power & Operation Section
        print("\n🔋 POWER & OPERATION")
        print("-" * 25)
        for key in ["fpwr", "fnst", "fnsp", "auto"]:
            if key in ps:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                value = DeviceStatePrinter.format_value(key, ps[key])
                print(f"  {desc:<20}: {value}")

        # Air Quality & Modes Section
        print("\n🌬️  AIR QUALITY & MODES")
        print("-" * 25)
        for key in ["nmod", "sltm", "rhtm"]:
            if key in ps:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                value = DeviceStatePrinter.format_value(key, ps[key])
                print(f"  {desc:<20}: {value}")

        # Oscillation & Direction Section
        print("\n🔄 OSCILLATION & DIRECTION")
        print("-" * 25)
        for key in ["oscs", "oson", "osal", "osau", "ancp"]:
            if key in ps:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                value = DeviceStatePrinter.format_value(key, ps[key])
                print(f"  {desc:<20}: {value}")

        # Filter Status Section
        print("\n🔧 FILTER STATUS")
        print("-" * 25)
        for key in ["hflr", "hflt", "cflr", "cflt"]:
            if key in ps:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                value = DeviceStatePrinter.format_value(key, ps[key])
                print(f"  {desc:<20}: {value}")

        # Network Information Section
        print("\n📡 NETWORK INFORMATION")
        print("-" * 25)
        for key in ["rssi", "channel"]:
            if key in msg:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                value = DeviceStatePrinter.format_value(key, msg[key])
                print(f"  {desc:<20}: {value}")

        # Device Information
        print("\n📱 DEVICE INFORMATION")
        print("-" * 25)
        if "time" in msg:
            print(f"  {'Last Update':<20}: {msg['time']}")
        if "mode-reason" in msg:
            print(f"  {'Mode Reason':<20}: {msg['mode-reason']}")
        if "state-reason" in msg:
            print(f"  {'State Reason':<20}: {msg['state-reason']}")

        print("=" * 50 + "\n")

    @staticmethod
    def print_state_change(msg: dict) -> None:
        """Print state changes with before/after values."""
        ps = msg.get("product-state", {})
        print("\n" + "=" * 50)
        print("         DYSON STATE CHANGE")
        print("=" * 50)

        changes = []
        for key, value in ps.items():
            if isinstance(value, list) and len(value) == 2:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                old_val = DeviceStatePrinter.format_value(key, value[0])
                new_val = DeviceStatePrinter.format_value(key, value[1])
                changes.append((desc, old_val, new_val))
            else:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                val = DeviceStatePrinter.format_value(key, value)
                changes.append((desc, "?", val))

        for desc, old_val, new_val in changes:
            if old_val != new_val:
                print(f"  {desc:<20}: {old_val} → {new_val}")
            else:
                print(f"  {desc:<20}: {new_val}")

        if "time" in msg:
            print(f"\n  {'Time':<20}: {msg['time']}")
        print("=" * 50 + "\n")

    @staticmethod
    def print_environmental(msg: dict) -> None:
        """Print environmental sensor data with proper formatting."""
        data = msg.get("data", {})
        print("\n" + "=" * 50)
        print("       ENVIRONMENTAL SENSOR DATA")
        print("=" * 50)

        print("\n🌡️  AIR QUALITY MEASUREMENTS")
        print("-" * 30)

        for key in ["pm25", "pm10", "p25r", "p10r"]:
            if key in data:
                desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get(key, key)
                value = DeviceStatePrinter.format_value(key, data[key])
                print(f"  {desc:<20}: {value}")

        # Sleep timer in environmental data
        if "sltm" in data:
            desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get("sltm", "sltm")
            value = DeviceStatePrinter.format_value("sltm", data["sltm"])
            print(f"  {desc:<20}: {value}")

        if "time" in msg:
            print(f"\n  {'Time':<20}: {msg['time']}")
        print("=" * 50 + "\n")

    @staticmethod
    def print_location(msg: dict) -> None:
        """Print device location/position information."""
        print("\n" + "=" * 50)
        print("         DEVICE LOCATION")
        print("=" * 50)

        if "apos" in msg:
            desc = DeviceStatePrinter.PARAM_DESCRIPTIONS.get("apos", "apos")
            value = DeviceStatePrinter.format_value("apos", msg["apos"])
            print(f"  {desc:<20}: {value}")

        if "time" in msg:
            print(f"  {'Time':<20}: {msg['time']}")
        print("=" * 50 + "\n")

    @staticmethod
    def print_any_message(msg: dict) -> None:
        """Smart printer that detects message type and formats appropriately."""
        msg_type = msg.get("msg", "UNKNOWN")

        if msg_type == "CURRENT-STATE":
            DeviceStatePrinter.print_current_state(msg)
        elif msg_type == "STATE-CHANGE":
            DeviceStatePrinter.print_state_change(msg)
        elif msg_type == "ENVIRONMENTAL-CURRENT-SENSOR-DATA":
            DeviceStatePrinter.print_environmental(msg)
        elif msg_type == "LOCATION":
            DeviceStatePrinter.print_location(msg)
        else:
            # Fallback for unknown message types
            print(f"\n=== {msg_type} ===")
            print(json.dumps(msg, indent=2))
            print("=" * (len(msg_type) + 8) + "\n")


class DeviceStateListener:
    """
    Thread-safe MQTT listener that maintains the latest device state.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current_state: Optional[Dict[str, Any]] = None
        self._environmental_data: Optional[Dict[str, Any]] = None
        self._last_update: Optional[float] = None
        self._client: Optional[DysonMQTTClient] = None
        self._listener_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    def _mqtt_callback(self, client: Any, userdata: Any, msg: Any) -> None:
        """Handle incoming MQTT messages and update state safely."""
        print(
            f"[DeviceStateListener] DEBUG: Received message on {msg.topic}: "
            f"{msg.payload}"
        )
        try:
            data = json.loads(msg.payload.decode(errors="replace"))
            msg_type = data.get("msg")

            with self._lock:
                if msg_type == "CURRENT-STATE":
                    self._current_state = data
                    self._last_update = time.time()
                    print("[DeviceStateListener] Updated current state")
                elif msg_type == "STATE-CHANGE":
                    # Update current state with changes
                    if self._current_state and "product-state" in data:
                        if "product-state" not in self._current_state:
                            self._current_state["product-state"] = {}

                        # Apply state changes
                        for key, value in data["product-state"].items():
                            if isinstance(value, list) and len(value) == 2:
                                # State change format: [old, new]
                                self._current_state["product-state"][key] = value[1]
                            else:
                                self._current_state["product-state"][key] = value

                        self._current_state["time"] = data.get("time")
                        self._last_update = time.time()
                        print("[DeviceStateListener] Applied state change")
                elif msg_type == "ENVIRONMENTAL-CURRENT-SENSOR-DATA":
                    self._environmental_data = data
                    self._last_update = time.time()
                    print("[DeviceStateListener] Updated environmental data")
                else:
                    print(f"[DeviceStateListener] Unknown message type: {msg_type}")

        except Exception as e:
            print(f"[DeviceStateListener] Parse error: {e}")

    def start(self) -> bool:
        """Start the listener in a background thread."""
        if self._running:
            return True

        if not ROOT_TOPIC or not SERIAL_NUMBER:
            raise ValueError("ROOT_TOPIC and SERIAL_NUMBER must be set.")

        try:
            self._client = DysonMQTTClient(client_id="d2mqtt-statelistener")
            topics = [
                f"{ROOT_TOPIC}/{SERIAL_NUMBER}/status/current",
                f"{ROOT_TOPIC}/{SERIAL_NUMBER}/status/fault",
            ]

            def listener_worker() -> None:
                try:
                    print("[DeviceStateListener] Starting listener worker...")

                    # Start the listener in the background
                    import threading

                    def delayed_request() -> None:
                        # Wait a few seconds for connection to establish
                        time.sleep(3)
                        print(
                            "[DeviceStateListener] Sending " "REQUEST-CURRENT-STATE..."
                        )
                        try:
                            self._client.send_command("REQUEST-CURRENT-STATE")
                        except Exception as e:
                            print(
                                f"[DeviceStateListener] Error sending request: " f"{e}"
                            )

                    # Start the delayed request in a separate thread
                    request_thread = threading.Thread(
                        target=delayed_request, daemon=True
                    )
                    request_thread.start()

                    # Use the working subscribe_and_listen pattern
                    self._client.subscribe_and_listen(topics, self._mqtt_callback)
                except Exception as e:
                    print(f"[DeviceStateListener] Error: {e}")

            self._stop_event.clear()
            self._listener_thread = threading.Thread(
                target=listener_worker, daemon=True
            )
            self._listener_thread.start()
            self._running = True

            # Give it a moment to connect
            time.sleep(1)
            return True

        except Exception as e:
            print(f"[DeviceStateListener] Failed to start: {e}")
            return False

    def stop(self) -> None:
        """Stop the listener thread."""
        if not self._running:
            return

        # The subscribe_and_listen method handles its own cleanup
        # We just need to mark as not running
        self._running = False

    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get the latest device state (thread-safe)."""
        with self._lock:
            return self._current_state.copy() if self._current_state else None

    def get_environmental_data(self) -> Optional[Dict[str, Any]]:
        """Get the latest environmental data (thread-safe)."""
        with self._lock:
            return self._environmental_data.copy() if self._environmental_data else None

    def get_last_update_time(self) -> Optional[float]:
        """Get the timestamp of the last update (thread-safe)."""
        with self._lock:
            return self._last_update

    def is_running(self) -> bool:
        """Check if the listener is running."""
        return self._running

    def wait_for_state(self, timeout: float = 10) -> bool:
        """Wait for initial state to be received."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.get_current_state():
                return True
            time.sleep(0.1)
        return False
