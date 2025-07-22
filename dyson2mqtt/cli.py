"""
CLI entry point for Dyson2MQTT modular app.
"""
import argparse
import logging
import sys
from dyson2mqtt.commands.power import set_power
from dyson2mqtt.commands.night_mode import set_night_mode
from dyson2mqtt.commands.auto_mode import set_auto_mode
from dyson2mqtt.commands.fan_speed import set_fan_speed
from dyson2mqtt.commands.sleep_timer import set_sleep_timer
from dyson2mqtt.commands.oscillation import (
    set_oscillation_angles, stop_oscillation, 
    get_oscillation_info, set_oscillation_width, set_oscillation_direction,
    WIDTH_DISPLAY_NAMES, parse_width_input, VALID_WIDTHS
)
from dyson2mqtt.state.device_state import DeviceStatePrinter
from dyson2mqtt.config import ROOT_TOPIC, SERIAL_NUMBER
from dyson2mqtt.mqtt.client import DysonMQTTClient
from dyson2mqtt.utils import parse_boolean
import json

def output_result(success: bool, message: str = "", data: dict = None, json_mode: bool = False):
    """Helper function for consistent output formatting."""
    if json_mode:
        result = {
            "success": success,
            "message": message
        }
        if data:
            result.update(data)
        print(json.dumps(result, indent=2))
    else:
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")

def parse_int_input(value) -> int:
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

def validate_oscillation_heading(heading_input) -> int:
    """
    Validate oscillation heading input.
    Returns validated heading as int.
    Raises ValueError for invalid input.
    """
    heading = parse_int_input(heading_input)
    if not (0 <= heading <= 359):
        raise ValueError("Heading must be between 0° and 359°")
    return heading

def validate_fan_speed_input(speed_input) -> int:
    """
    Validate fan speed input.
    Returns validated speed as int.
    Raises ValueError for invalid input.
    """
    speed = parse_int_input(speed_input)
    if not (0 <= speed <= 10):
        raise ValueError("Fan speed must be between 0 and 10")
    return speed

def main():
    parser = argparse.ArgumentParser(description="Dyson2MQTT Command Line Controller")
    parser.add_argument("--debug", action="store_true", help="Show debug output including MQTT logs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Power command
    power_parser = subparsers.add_parser("power", help="Turn power ON or OFF")
    power_parser.add_argument("state", help="Power state (on/off, true/false, 1/0, yes/no, y/n, t/f)")
    power_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")

    # Auto mode command
    auto_parser = subparsers.add_parser("auto", help="Set auto mode ON or OFF")
    auto_parser.add_argument("state", help="Auto mode state (on/off, true/false, 1/0, yes/no, y/n, t/f)")
    auto_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")

    # Night mode command
    night_parser = subparsers.add_parser("night", help="Set night mode ON or OFF")
    night_parser.add_argument("state", help="Night mode state (on/off, true/false, 1/0, yes/no, y/n, t/f)")
    night_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")

    # Fan speed command
    fan_parser = subparsers.add_parser("speed", help="Set fan speed (0-10). 0 will power off the fan.")
    fan_parser.add_argument("speed", help="Fan speed (0-10, can be string or number). 0 = off")
    fan_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")

    # Sleep timer command
    sleep_parser = subparsers.add_parser("timer", help="Set sleep timer (0-540 minutes, 0=off, or formats like 2h15m, 2:15, 1h, 45m)")
    sleep_parser.add_argument("minutes", type=str, metavar="MINUTES|2h15m|2:15|1h|45m|0", help="Sleep timer (e.g., 90, 2h15m, 2:15, 1h, 45m, 0=off)")
    sleep_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")

    # Listen command
    listen_parser = subparsers.add_parser("listen", help="Listen for Dyson status updates and pretty-print them")
    listen_parser.add_argument("--json", action="store_true", help="Output JSON messages instead of pretty-printed text")

    # Get state command  
    state_parser = subparsers.add_parser("state", help="Fetch current device state")
    state_parser.add_argument("--json", action="store_true", help="Output raw JSON instead of pretty-printed text")

    # Width command (oscillation width)
    width_parser = subparsers.add_parser("width", help="Set oscillation width centered on current position", aliases=["oscillation_width"])
    width_parser.add_argument("width", help="Oscillation width: numeric (0, 45, 90, 180, 350) or named (off, narrow, medium, wide, full)")
    width_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    
    # Direction command
    direction_parser = subparsers.add_parser("direction", help="Set oscillation direction while preserving current width")
    direction_parser.add_argument("direction", help="Center direction in degrees (0-359, can be string or number)")
    direction_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    
    # Stop oscillation command
    stop_parser = subparsers.add_parser("stop", help="Stop oscillation")
    stop_parser.add_argument("--json", action="store_true", help="Output JSON instead of text")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(level=logging.INFO)
    else:
        # Suppress MQTT client logs unless debugging
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('dyson2mqtt.mqtt.client').setLevel(logging.WARNING)

    try:
        if args.command == "power":
            try:
                # Validate input first
                from dyson2mqtt.utils import parse_boolean
                parse_boolean(args.state)  # This will raise ValueError if invalid
                success = set_power(args.state)
                output_result(success, f"Power set to {args.state.upper()}", json_mode=args.json)
            except ValueError as e:
                output_result(False, f"Invalid power state: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set power: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "auto":
            try:
                # Validate input first
                from dyson2mqtt.utils import parse_boolean
                parse_boolean(args.state)  # This will raise ValueError if invalid
                success = set_auto_mode(args.state)
                output_result(success, f"Auto mode set to {args.state.upper()}", json_mode=args.json)
            except ValueError as e:
                output_result(False, f"Invalid auto mode state: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set auto mode: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "night":
            try:
                # Validate input first
                from dyson2mqtt.utils import parse_boolean
                parse_boolean(args.state)  # This will raise ValueError if invalid
                success = set_night_mode(args.state)
                output_result(success, f"Night mode set to {args.state.upper()}", json_mode=args.json)
            except ValueError as e:
                output_result(False, f"Invalid night mode state: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set night mode: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "speed":
            try:
                validated_speed = validate_fan_speed_input(args.speed)
                success = set_fan_speed(validated_speed)
                output_result(success, f"Fan speed set to {validated_speed}", json_mode=args.json)
            except ValueError as e:
                output_result(False, f"Invalid fan speed: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set fan speed: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "timer":
            try:
                success = set_sleep_timer(args.minutes)
                output_result(success, f"Sleep timer set to {args.minutes}", json_mode=args.json)
            except ValueError as e:
                output_result(False, f"Invalid timer value: {e}", json_mode=args.json)
                sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set sleep timer: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "listen":
            try:
                client = DysonMQTTClient(client_id="d2mqtt-listen")
                client.connect()
                
                def pretty_callback(client_, userdata, msg):
                    try:
                        import json
                        data = json.loads(msg.payload.decode())
                        if args.json:
                            print(json.dumps(data, indent=2))
                        else:
                            if data.get("msg") == "STATE-CHANGE":
                                print(f"\n📊 State Change at {data.get('time', 'unknown')}")
                                if "product-state" in data:
                                    state = data["product-state"]
                                    print(f"  Power: {state.get('fpwr', ['UNKNOWN'])[1]}")
                                    print(f"  Fan Speed: {state.get('fnsp', ['UNKNOWN'])[1]}")
                                    print(f"  Auto Mode: {state.get('auto', ['UNKNOWN'])[1]}")
                                    print(f"  Night Mode: {state.get('nmod', ['UNKNOWN'])[1]}")
                                    print(f"  Oscillation: {state.get('oson', ['UNKNOWN'])[1]}")
                                    if state.get('oson', ['OFF'])[1] == 'ON':
                                        osal = state.get('osal', ['0000'])[1]
                                        osau = state.get('osau', ['0000'])[1]
                                        info = get_oscillation_info(osal, osau)
                                        print(f"  Oscillation Width: {info['width']}°")
                                        print(f"  Oscillation Heading: {info['heading']}°")
                                    print(f"  Sleep Timer: {state.get('sltm', ['UNKNOWN'])[1]}")
                            elif data.get("msg") == "LOCATION":
                                print(f"\n📍 Location: {data.get('apos', 'unknown')}°")
                            elif data.get("msg") == "CURRENT-STATE":
                                print(f"\n📋 Current State Response")
                                if "product-state" in data:
                                    state = data["product-state"]
                                    print(f"  Power: {state.get('fpwr', ['UNKNOWN'])[1]}")
                                    print(f"  Fan Speed: {state.get('fnsp', ['UNKNOWN'])[1]}")
                            else:
                                print(f"\n📨 Message: {data.get('msg', 'unknown')}")
                    except Exception as e:
                        print(f"Error parsing message: {e}")
                
                client.subscribe_and_listen(pretty_callback)
            except KeyboardInterrupt:
                print("\n👋 Stopping listener...")
                client.disconnect()
            except Exception as e:
                output_result(False, f"Failed to start listener: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "state":
            try:
                from dyson2mqtt.mqtt.async_client import async_get_state
                import asyncio
                
                async def run_async_get_state():
                    return await async_get_state()
                
                state = asyncio.run(run_async_get_state())
                if args.json:
                    print(json.dumps(state, indent=2))
                else:
                    if state and 'state' in state:
                        DeviceStatePrinter.print_current_state(state['state'])
                        if 'environmental' in state:
                            DeviceStatePrinter.print_environmental(state['environmental'])
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
                        raise ValueError(f"Width {parsed_width}° is not a valid Dyson step. Valid widths: {valid_names}")
                except ValueError as e:
                    output_result(False, f"Invalid width input: {e}", json_mode=args.json)
                    sys.exit(1)
                
                result = set_oscillation_width(args.width)
                if result["success"]:
                    width_name = WIDTH_DISPLAY_NAMES.get(result["actual_width"], f"{result['actual_width']}°")
                    message = f"Oscillation width set to {width_name}"
                    if result.get("adjusted"):
                        message += f" (adjusted from {result.get('requested_width', 'unknown')})"
                    output_result(True, message, result, json_mode=args.json)
                else:
                    output_result(False, f"Failed to set oscillation width: {result.get('error', 'Unknown error')}", result, json_mode=args.json)
                    sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set oscillation width: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "direction":
            try:
                # Validate heading input
                try:
                    validated_heading = validate_oscillation_heading(args.direction)
                except ValueError as e:
                    output_result(False, f"Invalid direction input: {e}", json_mode=args.json)
                    sys.exit(1)
                
                result = set_oscillation_direction(validated_heading)
                if result["success"]:
                    message = f"Oscillation direction set to {result['actual_heading']}°"
                    if result.get("adjusted"):
                        message += f" (adjusted from {result.get('original_heading', 'unknown')}°)"
                    output_result(True, message, result, json_mode=args.json)
                else:
                    output_result(False, f"Failed to set oscillation direction: {result.get('error', 'Unknown error')}", result, json_mode=args.json)
                    sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to set oscillation direction: {e}", json_mode=args.json)
                sys.exit(1)
        elif args.command == "stop":
            try:
                result = stop_oscillation()
                if result["success"]:
                    output_result(True, "Oscillation stopped", result, json_mode=args.json)
                else:
                    output_result(False, f"Failed to stop oscillation: {result.get('error', 'Unknown error')}", result, json_mode=args.json)
                    sys.exit(1)
            except Exception as e:
                output_result(False, f"Failed to stop oscillation: {e}", json_mode=args.json)
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