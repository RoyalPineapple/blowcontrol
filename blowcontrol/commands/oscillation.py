"""
Oscillation command module for Dyson2MQTT app.
"""

import logging
from typing import Any, Dict, Optional, Union

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


def set_oscillation_angles(
    width: Union[int, str], heading: Union[int, str] = 180
) -> dict:
    """
    Set oscillation angles (width and heading) for the Dyson device.

    Args:
        width: Oscillation width in degrees (0, 45, 90, 180, 350). 0 = no oscillation, just set heading.
        heading: Center direction in degrees (0-359, can be string or int)

    Returns:
        Dict with success, actual_width, actual_heading, lower_angle, upper_angle, adjusted

    Example:
        set_oscillation_angles(90, 180) → oscillates 135° to 225° (90° wide, center 180°)
        set_oscillation_angles(0, 90) → sets heading to 90° (no oscillation)
    """
    # Parse and validate inputs
    try:
        width_int = parse_int_input(width)
        heading_int = parse_int_input(heading)
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid input: {e}",
            "actual_width": None,
            "actual_heading": None,
            "lower_angle": None,
            "upper_angle": None,
            "adjusted": False,
            "original_heading": None,
        }

    # Validate inputs
    if width_int == 0:
        # Special case: width=0 means no oscillation, just set heading
        if not (0 <= heading_int <= 359):
            raise ValueError("Heading must be between 0° and 359°")

        logger.info(f"Setting heading to {heading_int}° with no oscillation (width=0)")

        # Try using STATE-SET with angles but keep oscillation off
        command_data = {
            "osal": f"{heading_int:04d}",
            "osau": f"{heading_int:04d}",
            "oscs": "OFF",
            "oson": "OFF",
        }

        try:
            client = DysonMQTTClient(client_id="d2mqtt-osc-heading")
            success = client.send_standalone_command("STATE-SET", command_data)

            if success:
                return {
                    "success": True,
                    "actual_width": 0,
                    "actual_heading": heading_int,
                    "lower_angle": heading_int,
                    "upper_angle": heading_int,
                    "adjusted": False,
                    "original_heading": None,
                    "message": f"Set heading to {heading_int}° (no oscillation)",
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to set heading",
                    "actual_width": None,
                    "actual_heading": None,
                    "lower_angle": None,
                    "upper_angle": None,
                    "adjusted": False,
                    "original_heading": None,
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error setting heading: {e}",
                "actual_width": None,
                "actual_heading": None,
                "lower_angle": None,
                "upper_angle": None,
                "adjusted": False,
                "original_heading": None,
            }

    # Normal oscillation case (width >= 45)
    if not (45 <= width_int <= 350):
        raise ValueError("Width must be between 45° and 350° (or 0 for no oscillation)")
    if not (0 <= heading_int <= 359):
        raise ValueError("Heading must be between 0° and 359°")

    # Calculate lower and upper angles
    half_width = width_int // 2
    lower_angle = (heading_int - half_width) % 360
    upper_angle = (heading_int + half_width) % 360
    original_heading = heading_int

    # Smart bounds adjustment: preserve width, adjust heading if needed
    # Dyson's bounds protection: 5° minimum, 355° maximum

    # Check if we need to adjust the heading to stay within bounds
    needs_adjustment = False

    if lower_angle > upper_angle:
        # Wrap-around case: would cross the forbidden zone
        needs_adjustment = True
    elif lower_angle < 5 or upper_angle > 355:
        # Normal case but out of bounds
        needs_adjustment = True

    if needs_adjustment:
        # Try to find a valid heading that preserves the width
        # First, check if the width itself is too large for any valid position
        if width_int > 350:  # 355 - 5 = 350° maximum possible width
            raise ValueError(
                f"Width {width_int}° is too large. Maximum width is 350° (5° to 355°)."
            )

        # Find the best heading that keeps the full width within 5°-355°
        # Strategy: try the closest valid positions to the original heading

        # Option 1: Adjust heading so lower bound is exactly 5°
        heading_option1 = (5 + half_width) % 360
        upper_option1 = (heading_option1 + half_width) % 360

        # Option 2: Adjust heading so upper bound is exactly 355°
        heading_option2 = (355 - half_width) % 360
        lower_option2 = (heading_option2 - half_width) % 360

        # Choose the option closest to the original heading
        def angle_distance(a1: int, a2: int) -> int:
            """Calculate the shortest angular distance between two angles."""
            diff = abs(a1 - a2)
            return min(diff, 360 - diff)

        dist1 = angle_distance(original_heading, heading_option1)
        dist2 = angle_distance(original_heading, heading_option2)

        # Validate both options and choose the best one
        valid_options = []

        # Option 1: Lower bound at 5°
        if upper_option1 <= 355:
            valid_options.append((heading_option1, dist1, "lower bound"))

        # Option 2: Upper bound at 355°
        if lower_option2 >= 5:
            valid_options.append((heading_option2, dist2, "upper bound"))

        if not valid_options:
            raise ValueError(
                f"Width {width_int}° cannot fit within Dyson's bounds (5°-355°) from any heading. Try a smaller width."
            )

        # Choose the closest valid option
        best_heading, best_distance, adjustment_type = min(
            valid_options, key=lambda x: x[1]
        )

        # Recalculate with the adjusted heading
        heading_int = best_heading
        lower_angle = (heading_int - half_width) % 360
        upper_angle = (heading_int + half_width) % 360

        logger.warning(
            f"Adjusted heading from {original_heading}° to {heading_int}° to fit width {width_int}° within bounds (adjusted {adjustment_type})"
        )

    # Final validation - this should always pass now
    if lower_angle > upper_angle or lower_angle < 5 or upper_angle > 355:
        raise ValueError(
            f"Internal error: failed to find valid heading for width {width_int}°"
        )

    # Handle wrap-around case (e.g., 350° to 10°) - only allowed if within
    # bounds
    if lower_angle > upper_angle:
        logger.warning(
            f"Wrap-around oscillation: {lower_angle}° to {upper_angle}° (width={width_int}°, heading={heading_int}°)"
        )

    logger.info(
        f"Setting oscillation: width={width_int}°, heading={heading_int}° -> angles {lower_angle}°-{upper_angle}°"
    )

    # Debug output
    if original_heading != heading_int:
        logger.info(
            f"Heading was adjusted from {original_heading}° to {heading_int}° (lower: {lower_angle}°, upper: {upper_angle}°)"
        )

    # Format as 4-digit strings with leading zeros
    osal = f"{lower_angle:04d}"
    osau = f"{upper_angle:04d}"

    # Create the STATE-SET command
    command_data = {
        "oscs": "ON",  # Enable oscillation
        "oson": "ON",  # Turn on oscillation
        "osal": osal,  # Lower angle
        "osau": osau,  # Upper angle
        "ancp": "CUST",  # Custom angle mode
    }

    try:
        client = DysonMQTTClient(client_id="d2mqtt-osc")
        success = client.send_standalone_command("STATE-SET", command_data)
        if success:
            logger.info(
                f"✅ Oscillation set: {lower_angle}°-{upper_angle}° (width={width_int}°, heading={heading_int}°)"
            )
        else:
            logger.error("❌ Failed to send oscillation command")

        return {
            "success": success,
            "actual_width": width_int,
            "actual_heading": heading_int,
            "lower_angle": lower_angle,
            "upper_angle": upper_angle,
            "adjusted": original_heading != heading_int,
            "original_heading": original_heading,
        }
    except Exception as e:
        logger.error(f"❌ Error setting oscillation: {e}")
        return {
            "success": False,
            "error": str(e),
            "actual_width": width_int,
            "actual_heading": heading_int,
            "lower_angle": None,
            "upper_angle": None,
            "adjusted": False,
            "original_heading": original_heading,
        }


def stop_oscillation() -> bool:
    """Stop oscillation (keep current position)."""
    command_data = {
        "oscs": "OFF",  # Disable oscillation
        "oson": "OFF",  # Turn off oscillation
    }

    try:
        client = DysonMQTTClient(client_id="d2mqtt-osc-stop")
        success = client.send_standalone_command("STATE-SET", command_data)
        if success:
            logger.info("✅ Oscillation stopped")
        else:
            logger.error("❌ Failed to stop oscillation")
        return success
    except Exception as e:
        logger.error(f"❌ Error stopping oscillation: {e}")
        return False


def get_oscillation_info(osal: str, osau: str) -> dict[str, Any]:
    """
    Convert raw oscillation angles back to width/heading format.

    Args:
        osal: Lower angle as 4-digit string (e.g., "0054")
        osau: Upper angle as 4-digit string (e.g., "0234")

    Returns:
        Dict with width, heading, lower_angle, upper_angle
    """
    lower = int(osal)
    upper = int(osau)

    # Calculate width and heading
    if lower <= upper:
        # Normal case: 90° to 270° = 180° width, 180° heading
        width = upper - lower
        heading = (lower + upper) // 2
    else:
        # Wrap-around case: 350° to 10° = 380° total, but 20° width
        width = (360 - lower) + upper
        heading = ((lower + upper + 360) // 2) % 360

    return {
        "width": width,
        "heading": heading,
        "lower_angle": lower,
        "upper_angle": upper,
        "is_wrap_around": lower > upper,
    }


# Dyson's valid oscillation width steps
VALID_WIDTHS = [0, 45, 90, 180, 350]

# Named width steps matching Dyson's terminology
WIDTH_NAMES = {"off": 0, "narrow": 45, "medium": 90, "wide": 180, "full": 350}

# Reverse mapping for display
WIDTH_DISPLAY_NAMES = {v: k for k, v in WIDTH_NAMES.items()}


def parse_width_input(width_input: Any) -> int:
    """
    Parse width input - can be numeric or named (off, narrow, medium, wide, full).

    Args:
        width_input: int or str representing the desired width

    Returns:
        int: The numeric width value

    Raises:
        ValueError: If the input is not a valid width or name
    """
    if isinstance(width_input, str):
        width_lower = width_input.lower()
        if width_lower in WIDTH_NAMES:
            return WIDTH_NAMES[width_lower]
        else:
            # Try to parse as numeric string
            try:
                return int(width_input)
            except ValueError:
                available_names = ", ".join(WIDTH_NAMES.keys())
                raise ValueError(
                    f"Invalid width name '{width_input}'. Valid names: {available_names}"
                )
    elif isinstance(width_input, int):
        return width_input
    else:
        raise ValueError(f"Width must be an integer or string, got {type(width_input)}")


def set_oscillation_width(
    width_input: Any, fallback_heading: int = 180
) -> dict[str, Any]:
    """
    Set oscillation width centered on current fan position (Dyson app style).

    Args:
        width_input: Oscillation width - can be numeric (0, 45, 90, 180, 350) or named (off, narrow, medium, wide, full)
        fallback_heading: Default heading if current position cannot be determined (default 180°)

    Returns:
        Dict with success, actual_width, actual_heading, lower_angle, upper_angle, adjusted

    Example:
        Fan at 128° → set_oscillation_width("medium") → oscillates 83° to 173°
        Fan at 128° → set_oscillation_width(90) → oscillates 83° to 173°
    """
    import asyncio

    from blowcontrol.mqtt.async_client import async_get_state

    # Parse the width input (numeric or named)
    try:
        width = parse_width_input(width_input)
        original_width_input = width_input
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "actual_width": None,
            "actual_heading": None,
            "lower_angle": None,
            "upper_angle": None,
            "adjusted": False,
            "original_heading": None,
            "width_adjusted": False,
            "requested_width": width_input,
            "adjusted_width": None,
        }

    # Validate and adjust width to match Dyson's steps
    original_width = width
    if width not in VALID_WIDTHS:
        # Find the next largest valid width
        valid_width = None
        for valid in VALID_WIDTHS:
            if valid >= width:
                valid_width = valid
                break

        if valid_width is None:
            # If larger than 350, use 350
            valid_width = 350

        width_name = WIDTH_DISPLAY_NAMES.get(valid_width, f"{valid_width}°")
        logger.warning(
            f"Width {width}° is not a valid Dyson step. Using {valid_width}° ({width_name}) instead. Valid: off, narrow, medium, wide, full"
        )
        width = valid_width

    # Handle special case: width 0 means turn off oscillation
    if width == 0:
        logger.info("Width 'off' requested - turning off oscillation")
        result = stop_oscillation_dict()
        result["width_adjusted"] = original_width != width
        result["requested_width"] = original_width_input
        result["adjusted_width"] = "off" if width == 0 else width
        return result

    # Try to get current fan position from device state
    current_heading = None
    try:
        logger.info("Getting current device state to determine fan position...")

        # Run the async state function
        async def get_state() -> Optional[Dict[str, Any]]:
            return await async_get_state(quiet=True)

        state_result = asyncio.run(get_state())

        if state_result and state_result.get("state"):
            state = state_result["state"]
            # Look for current position in the state - it might be in different fields
            # Check if oscillation is on and get the current angles

            # First try to get product-state data
            product_state = state.get("product-state", {})
            if product_state:
                if "osal" in product_state and "osau" in product_state:
                    # If oscillating, estimate center position
                    osal = int(product_state["osal"])
                    osau = int(product_state["osau"])
                    if osal <= osau:
                        current_heading = (osal + osau) // 2
                    else:
                        # Wrap-around case
                        current_heading = ((osal + osau + 360) // 2) % 360
                    logger.info(
                        f"Estimated current position from oscillation range: {current_heading}° (range: {osal}°-{osau}°)"
                    )
                elif "apos" in product_state:
                    # Direct position if available
                    current_heading = int(product_state["apos"])
                    logger.info(f"Current fan position from state: {current_heading}°")

            # Fallback to direct state fields if product-state not found
            if current_heading is None:
                if "osal" in state and "osau" in state:
                    # If oscillating, estimate center position
                    osal = int(state["osal"])
                    osau = int(state["osau"])
                    if osal <= osau:
                        current_heading = (osal + osau) // 2
                    else:
                        # Wrap-around case
                        current_heading = ((osal + osau + 360) // 2) % 360
                    logger.info(
                        f"Estimated current position from oscillation range: {current_heading}° (range: {osal}°-{osau}°)"
                    )
                elif "apos" in state:
                    # Direct position if available
                    current_heading = int(state["apos"])
                    logger.info(f"Current fan position from state: {current_heading}°")

            if current_heading is None:
                logger.warning("No position information found in device state")
                logger.debug(f"Available state keys: {list(state.keys())}")
                if product_state:
                    logger.debug(
                        f"Available product-state keys: {list(product_state.keys())}"
                    )

    except Exception as e:
        logger.warning(f"Could not get current position from state: {e}")

    # Use fallback if we couldn't get current position
    if current_heading is None:
        current_heading = fallback_heading
        logger.warning(
            f"Using fallback heading {fallback_heading}° (could not determine current position)"
        )

    # Use current or fallback position as heading and set the oscillation
    width_name = WIDTH_DISPLAY_NAMES.get(width, f"{width}°")
    logger.info(
        f"Setting {width}° ({width_name}) width centered on position {current_heading}°"
    )
    result = set_oscillation_angles(width, current_heading)

    # Add info about width adjustment if it occurred
    if original_width != width:
        result["width_adjusted"] = True
        result["requested_width"] = original_width_input
        result["adjusted_width"] = WIDTH_DISPLAY_NAMES.get(width, width)
    else:
        result["width_adjusted"] = False
        result["requested_width"] = original_width_input
        result["adjusted_width"] = WIDTH_DISPLAY_NAMES.get(width, width)

    return result


def stop_oscillation_dict() -> dict[str, Any]:
    """Stop oscillation and return dict format like set_oscillation_angles."""
    success = stop_oscillation()
    return {
        "success": success,
        "actual_width": 0,
        "actual_heading": None,
        "lower_angle": None,
        "upper_angle": None,
        "adjusted": False,
        "original_heading": None,
        "width_adjusted": False,
        "requested_width": 0,
        "adjusted_width": 0,
    }


def set_oscillation_direction(heading: Union[int, str]) -> dict[str, Any]:
    """
    Set oscillation heading (center direction) while preserving current width.
    If oscillation is currently off, just sets the heading without turning oscillation on.

    Args:
        heading: Center direction in degrees (0-359, can be string or int)

    Returns:
        Dict with success, actual_width, actual_heading, lower_angle, upper_angle, adjusted

    Example:
        Current: 135°-225° (90° wide, center 180°)
        set_oscillation_direction(270) → 225°-315° (90° wide, center 270°)

        Current: Oscillation OFF
        set_oscillation_direction(90) → Sets heading to 90° (oscillation remains OFF)
    """
    import asyncio

    from blowcontrol.mqtt.async_client import async_get_state

    # Parse and validate heading
    try:
        heading_int = parse_int_input(heading)
        if not (0 <= heading_int <= 359):
            return {
                "success": False,
                "error": "Heading must be between 0° and 359°",
                "actual_width": None,
                "actual_heading": None,
                "lower_angle": None,
                "upper_angle": None,
                "adjusted": False,
                "original_heading": None,
                "width_preserved": False,
                "current_width": None,
                "oscillation_was_off": False,
            }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid heading input: {e}",
            "actual_width": None,
            "actual_heading": None,
            "lower_angle": None,
            "upper_angle": None,
            "adjusted": False,
            "original_heading": None,
            "width_preserved": False,
            "current_width": None,
            "oscillation_was_off": False,
        }

    # Get current oscillation state from device
    current_width = None
    oscillation_is_on = False
    try:
        logger.info("Getting current device state to determine oscillation status...")

        # Run the async state function
        async def get_state() -> Optional[Dict[str, Any]]:
            return await async_get_state(quiet=True)

        state_result = asyncio.run(get_state())

        if state_result and state_result.get("state"):
            state = state_result["state"]

            # Check if oscillation is currently on
            product_state = state.get("product-state", {})
            if product_state:
                oscs = product_state.get("oscs", "OFF")
                oson = product_state.get("oson", "OFF")

                if oscs == "ON" and oson == "ON":
                    oscillation_is_on = True
                    # Get current oscillation angles
                    if "osal" in product_state and "osau" in product_state:
                        osal = int(product_state["osal"])
                        osau = int(product_state["osau"])

                        # Calculate current width
                        if osal <= osau:
                            current_width = osau - osal
                        else:
                            # Wrap-around case
                            current_width = (360 - osal) + osau

                        logger.info(
                            f"Current oscillation: {osal}°-{osau}° (width: {current_width}°)"
                        )
                    else:
                        logger.warning("Oscillation is on but no angle data found")
                else:
                    logger.info(
                        "Oscillation is currently off - will just set heading without turning oscillation on"
                    )

            # Fallback to direct state fields if product-state not found
            if current_width is None and oscillation_is_on:
                oscs = state.get("oscs", "OFF")
                oson = state.get("oson", "OFF")

                if (
                    oscs == "ON"
                    and oson == "ON"
                    and "osal" in state
                    and "osau" in state
                ):
                    osal = int(state["osal"])
                    osau = int(state["osau"])

                    if osal <= osau:
                        current_width = osau - osal
                    else:
                        current_width = (360 - osal) + osau

                    logger.info(
                        f"Current oscillation: {osal}°-{osau}° (width: {current_width}°)"
                    )

    except Exception as e:
        logger.warning(f"Could not get current oscillation state: {e}")

    # If oscillation is off, use the sweep pattern to set heading without
    # turning oscillation on
    if not oscillation_is_on:
        logger.info(
            f"Oscillation is off - setting heading to {heading_int}° using sweep pattern"
        )

        # Use the pattern from sweep.txt: set both angles to heading with oson=ON
        # But also explicitly set oscs=OFF to keep oscillation off
        command_data = {
            "osal": f"{heading_int:04d}",
            "osau": f"{heading_int:04d}",
            "oson": "ON",
            "oscs": "OFF",
            "ancp": "CUST",
        }

        try:
            client = DysonMQTTClient(client_id="d2mqtt-osc-heading-off")
            success = client.send_standalone_command("STATE-SET", command_data)

            if success:
                logger.info(
                    f"✅ Set heading to {heading_int}° (oscillation remains off)"
                )
                return {
                    "success": True,
                    "actual_width": 0,
                    "actual_heading": heading_int,
                    "lower_angle": heading_int,
                    "upper_angle": heading_int,
                    "adjusted": False,
                    "original_heading": None,
                    "width_preserved": False,
                    "current_width": 0,
                    "oscillation_was_off": True,
                    "message": f"Set heading to {heading_int}° (oscillation remains off)",
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to set heading",
                    "actual_width": None,
                    "actual_heading": None,
                    "lower_angle": None,
                    "upper_angle": None,
                    "adjusted": False,
                    "original_heading": None,
                    "width_preserved": False,
                    "current_width": None,
                    "oscillation_was_off": True,
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error setting heading: {e}",
                "actual_width": None,
                "actual_heading": None,
                "lower_angle": None,
                "upper_angle": None,
                "adjusted": False,
                "original_heading": None,
                "width_preserved": False,
                "current_width": None,
                "oscillation_was_off": True,
            }

    # Oscillation is on - preserve current width and set new heading
    if current_width is None:
        current_width = 90  # Default to medium width
        logger.warning(
            f"Using default width {current_width}° (could not determine current width)"
        )
        width_preserved = False
    else:
        width_preserved = True

    # Validate the width is a valid Dyson step
    if current_width not in VALID_WIDTHS:
        # Find the closest valid width
        closest_width = min(VALID_WIDTHS, key=lambda x: abs(x - current_width))
        logger.warning(
            f"Current width {current_width}° is not a valid step, using closest: {closest_width}°"
        )
        current_width = closest_width

    # Set oscillation with preserved width and new heading
    width_name = WIDTH_DISPLAY_NAMES.get(current_width, f"{current_width}°")
    logger.info(
        f"Setting heading to {heading_int}° while preserving {current_width}° ({width_name}) width"
    )

    result = set_oscillation_angles(current_width, heading_int)

    # Add heading-specific info
    result["width_preserved"] = width_preserved
    result["current_width"] = current_width
    result["requested_heading"] = heading_int
    result["oscillation_was_off"] = False

    return result
