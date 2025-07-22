"""
Utility functions for Dyson2MQTT.
"""

def parse_boolean(value) -> bool:
    """
    Parse flexible boolean input into a boolean value.
    
    Supports:
    - True/False (Python bool)
    - "true"/"false" (case insensitive)
    - "t"/"f" (case insensitive)
    - "1"/"0"
    - "on"/"off" (case insensitive)
    - "yes"/"no" (case insensitive)
    - "y"/"n" (case insensitive)
    
    Args:
        value: The value to parse
        
    Returns:
        bool: True or False
        
    Raises:
        ValueError: If the value cannot be parsed as a boolean
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value_lower = value.lower().strip()
        
        # True values
        if value_lower in ('true', 't', '1', 'on', 'yes', 'y'):
            return True
        
        # False values
        if value_lower in ('false', 'f', '0', 'off', 'no', 'n'):
            return False
    
    elif isinstance(value, int):
        if value == 1:
            return True
        elif value == 0:
            return False
    
    raise ValueError(f"Cannot parse '{value}' as boolean. Supported formats: true/false, t/f, 1/0, on/off, yes/no, y/n") 