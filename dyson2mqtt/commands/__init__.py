"""
Device Command Modules

Individual command implementations for controlling Dyson device features.

Available Commands:
    - power: Turn device on/off
    - auto_mode: Enable/disable auto mode
    - night_mode: Enable/disable night mode
    - fan_speed: Set fan speed (1-10)
    - sleep_timer: Set/clear sleep timer
    - oscillation: Control oscillation with width/direction model
"""

from .auto_mode import set_auto_mode
from .fan_speed import set_fan_speed
from .night_mode import set_night_mode
from .oscillation import (
    set_oscillation_angles,
    set_oscillation_direction,
    set_oscillation_width,
    stop_oscillation,
)
from .power import request_current_state, set_power
from .sleep_timer import set_sleep_timer

__all__ = [
    "set_power",
    "request_current_state",
    "set_auto_mode",
    "set_night_mode",
    "set_fan_speed",
    "set_sleep_timer",
    "set_oscillation_angles",
    "stop_oscillation",
    "set_oscillation_width",
    "set_oscillation_direction"
]
