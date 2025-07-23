"""
Dyson2MQTT - Professional Dyson Fan Controller

A modular Python application for controlling Dyson fans via MQTT with support
for real-time monitoring, async operations, and machine-readable JSON output.

Usage:
    python3 -m app <command> [arguments]

Example:
    python3 -m app power on
    python3 -m app async-get-state --json
"""

__version__ = "1.0.0"
__author__ = "Alex Odawa"
__license__ = "MIT"
__url__ = "https://github.com/yourusername/dyson2mqtt"

# Main CLI entry point
from .cli import main

__all__ = ["main"]
