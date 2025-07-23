"""
CLI entry point for Dyson2MQTT modular app.
"""

import argparse
import json
import logging
import sys
from typing import Any, Dict, Optional

from dyson2mqtt.commands.auto_mode import set_auto_mode
from dyson2mqtt.commands.fan_speed import set_fan_speed
from dyson2mqtt.commands.night_mode import set_night_mode
from dyson2mqtt.commands.oscillation import (
    VALID_WIDTHS,
    WIDTH_DISPLAY_NAMES,
    get_oscillation_info,
    parse_width_input,
    set_oscillation_direction,
    set_oscillation_width,
    stop_oscillation_dict,
)
from dyson2mqtt.commands.power import set_power
from dyson2mqtt.commands.sleep_timer import set_sleep_timer
from dyson2mqtt.mqtt.client import DysonMQTTClient
from dyson2mqtt.state.device_state import DeviceStatePrinter
from dyson2mqtt.utils import parse_boolean


def output_result(
    success: bool,
    message: str = "",
    data: Optional[dict] = None,
    json_mode: bool = False,
) -> None:
    """Helper function for consistent output formatting."""
    if json_mode:
        result = {"success": success, "message": message}
        if data:
            result.update(data)
        print(json.dumps(result, indent=2))
    else:
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")


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


def validate_oscillation_heading(heading_input: Any) -> int:
    """
    Validate oscillation heading input.
    Returns validated heading as int.
    Raises ValueError for invalid input.
    """
    heading = parse_int_input(heading_input)
    if not (0 <= heading <= 359):
        raise ValueError("Heading must be between 0° and 359°")
    return heading


def validate_fan_speed_input(speed_input: Any) -> int:
    """
    Validate fan speed input.
    Returns validated speed as int.
    Raises ValueError for invalid input.
    """
    speed = parse_int_input(speed_input)
    if not (0 <= speed <= 10):
        raise ValueError("Fan speed must be between 0 and 10")
    return speed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dyson2MQTT - Control Dyson fans via MQTT",
        epilog="""
EXAMPLES:
  # Basic control
  dyson2mqtt power on                    # Turn fan on
  dyson2mqtt speed 5                     # Set speed to 5
  dyson2mqtt auto on                     # Enable auto mode
  dyson2mqtt night on                    # Enable night mode
  dyson2mqtt timer 2h15m                 # Set 2h15m sleep timer

  # Oscillation control
  dyson2mqtt width wide                  # Set wide oscillation
  dyson2mqtt direction 180               # Point oscillation at 180°
  dyson2mqtt stop                        # Stop oscillation

  # Monitoring
  dyson2mqtt listen                      # Real-time status updates
  dyson2mqtt state --json                # Get current state as JSON

  # Automation
  dyson2mqtt power on --json             # JSON output for scripts
  STATUS=$(dyson2mqtt state --json)      # Capture state in variable

CONFIGURATION:
  Set environment variables or create .env file:
    DEVICE_IP=192.168.1.100
    MQTT_PORT=1883
    MQTT_PASSWORD=your-password
    ROOT_TOPIC=438M
    SERIAL_NUMBER=your-device-serial

EXIT CODES:
  0  Success
  1  Error (invalid input, connection failure, etc.)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output including MQTT logs",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Power command
    power_parser = subparsers.add_parser(
        "power",
        help="Turn device power ON or OFF",
        description="Control device power state. Accepts various boolean formats.",
    )
    power_parser.add_argument(
        "state", help="Power state: on/off, true/false, 1/0, yes/no, y/n, t/f"
    )
    power_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON (useful for automation)",
    )

    # Auto mode command
    auto_parser = subparsers.add_parser(
        "auto",
        help="Enable or disable auto mode",
        description=(
            "Auto mode automatically adjusts fan speed based on environmental "
            "conditions."
        ),
    )
    auto_parser.add_argument(
        "state",
        help="Auto mode state: on/off, true/false, 1/0, yes/no, y/n, t/f",
    )
    auto_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    # Night mode command
    night_parser = subparsers.add_parser(
        "night",
        help="Enable or disable night mode",
        description="Night mode reduces noise and airflow for quiet operation.",
    )
    night_parser.add_argument(
        "state",
        help="Night mode state: on/off, true/false, 1/0, yes/no, y/n, t/f",
    )
    night_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    # Fan speed command
    fan_parser = subparsers.add_parser(
        "speed",
        help="Set fan speed (0-10)",
        description=(
            "Set fan speed from 0 (off) to 10 (maximum). Speed 0 will power "
            "off the fan."
        ),
    )
    fan_parser.add_argument("speed", help="Fan speed: 0-10 (0 = off, 10 = maximum)")
    fan_parser.add_argument("--json", action="store_true", help="Output result as JSON")

    # Sleep timer command
    sleep_parser = subparsers.add_parser(
        "timer",
        help="Set sleep timer",
        description=(
            "Set sleep timer to automatically turn off the device. Range: "
            "0-540 minutes."
        ),
    )
    sleep_parser.add_argument(
        "minutes",
        type=str,
        metavar="TIME",
        help="Timer duration: 90, 2h15m, 2:15, 1h, 45m, 0 (off)",
    )
    sleep_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    # Listen command
    listen_parser = subparsers.add_parser(
        "listen",
        help="Monitor device status in real-time",
        description=(
            "Listen for MQTT status updates and display them in real-time. "
            "Press Ctrl+C to stop."
        ),
    )
    listen_parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON messages instead of formatted text",
    )

    # Get state command
    state_parser = subparsers.add_parser(
        "state",
        help="Fetch current device state",
        description=(
            "Retrieve and display the current device state including power, "
            "speed, modes, and environmental data."
        ),
    )
    state_parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted display",
    )

    # Width command (oscillation width)
    width_parser = subparsers.add_parser(
        "width",
        help="Set oscillation width",
        description=(
            "Set oscillation width centered on current position. Can use "
            "numeric values or named presets."
        ),
        aliases=["oscillation_width"],
    )
    width_parser.add_argument(
        "width", help="Width: 0,45,90,180,350 or off,narrow,medium,wide,full"
    )
    width_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    # Direction command
    direction_parser = subparsers.add_parser(
        "direction",
        help="Set oscillation direction",
        description=(
            "Set oscillation direction while preserving current width. "
            "Direction is in degrees."
        ),
    )
    direction_parser.add_argument("direction", help="Direction in degrees: 0-359")
    direction_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    # Stop oscillation command
    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop oscillation",
        description="Stop all oscillation movement. The device will remain stationary.",
    )
    stop_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    # Parse arguments
    args = parser.parse_args()

    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(level=logging.INFO)
    else:
        # Suppress MQTT client logs unless debugging
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("dyson2mqtt.mqtt.client").setLevel(logging.WARNING)

    try:
        if args.command == "power":
            try:
                # Validate input first
                parse_boolean(args.state)  # This will raise ValueError if invalid
                success = set_power(args.state)
                output_result(
                    success,
                    f"Power set to {args.state.upper()}",
                    json_mode=args.json,
                )
            except ValueError as e:
                output_result(False, f"Invalid power state: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set power: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "auto":
            try:
                # Validate input first
                parse_boolean(args.state)  # This will raise ValueError if invalid
                success = set_auto_mode(args.state)
                output_result(
                    success,
                    f"Auto mode set to {args.state.upper()}",
                    json_mode=args.json,
                )
            except ValueError as e:
                output_result(
                    False, f"Invalid auto mode state: {e}", json_mode=args.json
                )
                sys.exit(1)
            except Exception as e:
                output_result(
                    False, f"Failed to set auto mode: {e}", json_mode=args.json
                )
                sys.exit(1)
        elif args.command == "night":
            try:
                # Validate input first
                parse_boolean(args.state)  # This will raise ValueError if invalid
                success = set_night_mode(args.state)
                output_result(
                    success,
                    f"Night mode set to {args.state.upper()}",
                    json_mode=args.json,
                )
            except ValueError as e:
                output_result(
                    False,
                    f"Invalid night mode state: {e}",
                    json_mode=args.json,
                )
                sys.exit(1)
            except Exception as e:
                output_result(
                    False,
                    f"Failed to set night mode: {e}",
                    json_mode=args.json,
                )
                sys.exit(1)
        elif args.command == "speed":
            try:
                validated_speed = validate_fan_speed_input(args.speed)
                success = set_fan_speed(validated_speed)
                output_result(
                    success,
                    f"Fan speed set to {validated_speed}",
                    json_mode=args.json,
                )
            except ValueError as e:
                output_result(False, f"Invalid fan speed: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(
                    False, f"Failed to set fan speed: {e}", json_mode=args.json
                )
                sys.exit(1)
        elif args.command == "timer":
            try:
                success = set_sleep_timer(args.minutes)
                output_result(
                    success,
                    f"Sleep timer set to {args.minutes}",
                    json_mode=args.json,
                )
            except ValueError as e:
                output_result(False, f"Invalid timer value: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(
                    False,
                    f"Failed to set sleep timer: {e}",
                    json_mode=args.json,
                )
                sys.exit(1)
        elif args.command == "listen":
            try:
                client = DysonMQTTClient(client_id="d2mqtt-listen")
                client.connect()

                def pretty_callback(client_: Any, userdata: Any, msg: Any) -> None:
                    """Pretty print MQTT messages."""
                    try:
                        data = json.loads(msg.payload.decode(errors="replace"))
                        if args.json:
                            print(json.dumps(data, indent=2))
                        else:
                            if data.get("msg") == "STATE-CHANGE":
                                print(
                                    f"\n📊 State Change at {data.get('time', 'unknown')}"
                                )
                                if "product-state" in data:
                                    state = data["product-state"]
                                    print(
                                        f"  Power: {state.get('fpwr', ['UNKNOWN'])[1]}"
                                    )
                                    print(
                                        f"  Fan Speed: {state.get('fnsp', ['UNKNOWN'])[1]}"
                                    )
                                    print(
                                        f"  Auto Mode: {state.get('auto', ['UNKNOWN'])[1]}"
                                    )
                                    print(
                                        f"  Night Mode: {state.get('nmod', ['UNKNOWN'])[1]}"
                                    )
                                    print(
                                        f"  Oscillation: {state.get('oson', ['UNKNOWN'])[1]}"
                                    )
                                    if state.get("oson", ["OFF"])[1] == "ON":
                                        osal = state.get("osal", ["0000"])[1]
                                        osau = state.get("osau", ["0000"])[1]
                                        info = get_oscillation_info(osal, osau)
                                        print(f"  Oscillation Width: {info['width']}°")
                                        print(
                                            f"  Oscillation Heading: {info['heading']}°"
                                        )
                                    print(
                                        f"  Sleep Timer: {state.get('sltm', ['UNKNOWN'])[1]}"
                                    )
                            elif data.get("msg") == "LOCATION":
                                print(f"\n📍 Location: {data.get('apos', 'unknown')}°")
                            elif data.get("msg") == "CURRENT-STATE":
                                print("\n📋 Current State Response")
                                if "product-state" in data:
                                    state = data["product-state"]
                                    print(
                                        f"  Power: {state.get('fpwr', ['UNKNOWN'])[1]}"
                                    )
                                    print(
                                        f"  Fan Speed: {state.get('fnsp', ['UNKNOWN'])[1]}"
                                    )
                            else:
                                print(f"\n📨 Message: {data.get('msg', 'unknown')}")
                    except Exception as e:
                        print(f"Error parsing message: {e}")

                def json_callback(client_: Any, userdata: Any, msg: Any) -> None:
                    """Output raw JSON MQTT messages."""
                    try:
                        data = json.loads(msg.payload.decode(errors="replace"))
                        print(json.dumps(data, indent=2))
                    except Exception as e:
                        print(f"Error parsing message: {e}")

                callback = json_callback if args.json else pretty_callback

                client.subscribe_and_listen(
                    ["status/current", "status/fault"], callback
                )
            except KeyboardInterrupt:
                print("\n👋 Stopping listener...")
                client.disconnect()
            except Exception as e:
                output_result(
                    False,
                    f"Failed to start listener: {e}",
                    json_mode=args.json,
                )
                sys.exit(1)
        elif args.command == "state":
            try:
                import asyncio

                from dyson2mqtt.mqtt.async_client import async_get_state

                async def run_async_get_state() -> Optional[Dict[str, Any]]:
                    """Async function to get device state."""
                    return await async_get_state()

                state = asyncio.run(run_async_get_state())
                if args.json:
                    print(json.dumps(state, indent=2))
                else:
                    if state and "state" in state:
                        DeviceStatePrinter.print_current_state(state["state"])
                        if "environmental" in state:
                            DeviceStatePrinter.print_environmental(
                                state["environmental"]
                            )
                    else:
                        print("No state received from device.")
            except Exception as e:
                output_result(False, f"Failed to get state: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "width":
            try:
                # Validate width input
                try:
                    parsed_width = parse_width_input(args.width)
                    if parsed_width not in VALID_WIDTHS:
                        valid_names = ", ".join([f"{w}°" for w in VALID_WIDTHS])
                        raise ValueError(
                            f"Width {parsed_width}° is not a valid Dyson step. "
                            f"Valid widths: {valid_names}"
                        )
                except ValueError as e:
                    output_result(
                        False, f"Invalid width input: {e}", json_mode=args.json
                    )
                    sys.exit(1)

                result = set_oscillation_width(args.width)
                if result["success"]:
                    width_name = WIDTH_DISPLAY_NAMES.get(
                        result["actual_width"], f"{result['actual_width']}°"
                    )
                    message = f"Oscillation width set to {width_name}"
                    if result.get("adjusted"):
                        message += f" (adjusted from {result.get('requested_width', 'unknown')})"
                    output_result(True, message, result, json_mode=args.json)
                else:
                    output_result(
                        False,
                        f"Failed to set oscillation width: "
                        f"{result.get('error', 'Unknown error')}",
                        result,
                        json_mode=args.json,
                    )
                    sys.exit(1)
            except Exception as e:
                output_result(
                    False,
                    f"Failed to set oscillation width: {e}",
                    json_mode=args.json,
                )
                sys.exit(1)
        elif args.command == "direction":
            try:
                # Validate heading input
                try:
                    validated_heading = validate_oscillation_heading(args.direction)
                except ValueError as e:
                    output_result(
                        False,
                        f"Invalid direction input: {e}",
                        json_mode=args.json,
                    )
                    sys.exit(1)

                result = set_oscillation_direction(validated_heading)
                if result["success"]:
                    message = (
                        f"Oscillation direction set to {validated_heading}° "
                        f"(adjusted from {result.get('requested_heading', 'unknown')})"
                    )
                    if result.get("adjusted"):
                        message += f" (adjusted from {result.get('original_heading', 'unknown')}°)"
                    output_result(True, message, result, json_mode=args.json)
                else:
                    output_result(
                        False,
                        f"Failed to set oscillation direction: {result.get('error', 'Unknown error')}",
                        result,
                        json_mode=args.json,
                    )
                    sys.exit(1)
            except Exception as e:
                output_result(
                    False,
                    f"Failed to set oscillation direction: {e}",
                    json_mode=args.json,
                )
                sys.exit(1)
        elif args.command == "stop":
            try:
                result = stop_oscillation_dict()
                if result["success"]:
                    output_result(
                        True,
                        "Oscillation stopped",
                        result,
                        json_mode=args.json,
                    )
                else:
                    output_result(
                        False,
                        f"Failed to stop oscillation: {result.get('error', 'Unknown error')}",
                        result,
                        json_mode=args.json,
                    )
                    sys.exit(1)
            except Exception as e:
                output_result(
                    False,
                    f"Failed to stop oscillation: {e}",
                    json_mode=args.json,
                )
                sys.exit(1)
        else:
            print(f"Error: Unknown command '{args.command}'")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
