"""
Unit tests for command modules.
"""

import pytest
from unittest.mock import Mock, patch
from dyson2mqtt.commands.power import set_power, request_current_state
from dyson2mqtt.commands.fan_speed import set_fan_speed, validate_fan_speed
from dyson2mqtt.commands.auto_mode import set_auto_mode
from dyson2mqtt.commands.night_mode import set_night_mode
from dyson2mqtt.commands.sleep_timer import set_sleep_timer, parse_sleep_time
from dyson2mqtt.commands.oscillation import (
    set_oscillation_angles, 
    stop_oscillation, 
    get_oscillation_info,
    parse_width_input,
    set_oscillation_width,
    set_oscillation_direction,
    stop_oscillation_dict,
    VALID_WIDTHS,
    WIDTH_NAMES,
    WIDTH_DISPLAY_NAMES
)


class TestPowerCommands:
    """Test power control commands."""

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.power.DysonMQTTClient')
    def test_set_power_on(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting power ON."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_power(True)
        
        assert result is True
        mock_client.connect.assert_called_once()
        mock_client.set_boolean_state.assert_called_once_with('fpwr', True)
        mock_client.disconnect.assert_called_once()

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.power.DysonMQTTClient')
    def test_set_power_off(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting power OFF."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_power(False)
        
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('fpwr', False)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.power.DysonMQTTClient')
    def test_set_power_flexible_inputs(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test power command with various flexible boolean inputs."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Test string inputs
        for true_input in ["true", "TRUE", "t", "T", "1", "on", "ON", "yes", "YES", "y", "Y"]:
            mock_client.reset_mock()
            result = set_power(true_input)
            assert result is True
            mock_client.set_boolean_state.assert_called_once_with('fpwr', True)
        
        # Test various false inputs
        for false_input in ["false", "FALSE", "f", "F", "0", "off", "OFF", "no", "NO", "n", "N"]:
            mock_client.reset_mock()
            result = set_power(false_input)
            assert result is True
            mock_client.set_boolean_state.assert_called_once_with('fpwr', False)
        
        # Test integer inputs
        mock_client.reset_mock()
        result = set_power(1)
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('fpwr', True)
        
        mock_client.reset_mock()
        result = set_power(0)
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('fpwr', False)
        
        # Test boolean inputs
        mock_client.reset_mock()
        result = set_power(True)
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('fpwr', True)
        
        mock_client.reset_mock()
        result = set_power(False)
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('fpwr', False)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.power.DysonMQTTClient')
    def test_set_power_error(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test power command error handling."""
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client
        
        result = set_power(True)
        
        assert result is False

    def test_set_power_invalid_boolean(self):
        """Test power command with invalid boolean input."""
        result = set_power("invalid")
        assert result is False

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.power.DysonMQTTClient')
    def test_request_current_state(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test requesting current state."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        request_current_state()
        
        mock_client.connect.assert_called_once()
        mock_client.send_command.assert_called_once_with("REQUEST-CURRENT-STATE")
        mock_client.disconnect.assert_called_once()


class TestFanSpeedCommands:
    """Test fan speed control commands."""

    def test_validate_fan_speed_valid(self):
        """Test valid fan speed validation."""
        assert validate_fan_speed(0) == 0
        assert validate_fan_speed(5) == 5
        assert validate_fan_speed(10) == 10

    def test_validate_fan_speed_invalid_type(self):
        """Test fan speed validation with invalid types."""
        with pytest.raises(ValueError, match="Cannot convert"):
            validate_fan_speed(5.5)
        with pytest.raises(ValueError, match="Cannot convert"):
            validate_fan_speed(None)
        with pytest.raises(ValueError, match="invalid literal for int"):
            validate_fan_speed("invalid")

    def test_validate_fan_speed_flexible_input(self):
        """Test fan speed validation with flexible input types."""
        # Test string inputs
        assert validate_fan_speed("5") == 5
        assert validate_fan_speed("0") == 0
        assert validate_fan_speed("10") == 10
        
        # Test integer inputs
        assert validate_fan_speed(5) == 5
        assert validate_fan_speed(0) == 0
        assert validate_fan_speed(10) == 10

    def test_validate_fan_speed_invalid_range(self):
        """Test fan speed validation with invalid range."""
        with pytest.raises(ValueError, match="Fan speed must be between 0 and 10"):
            validate_fan_speed(-1)
        with pytest.raises(ValueError, match="Fan speed must be between 0 and 10"):
            validate_fan_speed(11)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.fan_speed.DysonMQTTClient')
    def test_set_fan_speed_valid(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting valid fan speed."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_fan_speed(5)
        
        assert result is True
        mock_client.set_numeric_state.assert_called_once_with('fnsp', '0005')

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.fan_speed.set_power')
    @patch('dyson2mqtt.commands.fan_speed.DysonMQTTClient')
    def test_set_fan_speed_zero(self, mock_client_class, mock_set_power, mock_paho_client, mock_env_vars):
        """Test setting fan speed to 0 (power off)."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_set_power.return_value = True
        
        result = set_fan_speed(0)
        
        assert result is True
        mock_set_power.assert_called_once_with(False)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.fan_speed.DysonMQTTClient')
    def test_set_fan_speed_invalid(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting invalid fan speed."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # set_fan_speed catches ValueError and returns False
        result = set_fan_speed(11)
        assert result is False
        
        result = set_fan_speed(-1)
        assert result is False

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.fan_speed.DysonMQTTClient')
    def test_set_fan_speed_error(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test fan speed command error handling."""
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client
        
        result = set_fan_speed(5)
        
        assert result is False


class TestAutoModeCommands:
    """Test auto mode control commands."""

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.auto_mode.DysonMQTTClient')
    def test_set_auto_mode_on(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting auto mode ON."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_auto_mode(True)
        
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('auto', True)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.auto_mode.DysonMQTTClient')
    def test_set_auto_mode_off(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting auto mode OFF."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_auto_mode(False)
        
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('auto', False)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.auto_mode.DysonMQTTClient')
    def test_set_auto_mode_error(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test auto mode command error handling."""
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client
        
        result = set_auto_mode(True)
        
        assert result is False


class TestNightModeCommands:
    """Test night mode control commands."""

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.night_mode.DysonMQTTClient')
    def test_set_night_mode_on(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting night mode ON."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_night_mode(True)
        
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('nmod', True)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.night_mode.DysonMQTTClient')
    def test_set_night_mode_off(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting night mode OFF."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_night_mode(False)
        
        assert result is True
        mock_client.set_boolean_state.assert_called_once_with('nmod', False)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.night_mode.DysonMQTTClient')
    def test_set_night_mode_error(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test night mode command error handling."""
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client
        
        result = set_night_mode(True)
        
        assert result is False


class TestSleepTimerCommands:
    """Test sleep timer control commands."""

    def test_parse_sleep_time_minutes(self):
        """Test parsing sleep time in minutes."""
        assert parse_sleep_time(30) == 30
        assert parse_sleep_time("30") == 30
        assert parse_sleep_time("0") == 0

    def test_parse_sleep_time_hours_minutes(self):
        """Test parsing sleep time in hours:minutes format."""
        assert parse_sleep_time("2:30") == 150
        assert parse_sleep_time("1:05") == 65
        assert parse_sleep_time("0:45") == 45

    def test_parse_sleep_time_hours(self):
        """Test parsing sleep time with hours."""
        assert parse_sleep_time("2h") == 120
        assert parse_sleep_time("1h30m") == 90
        assert parse_sleep_time("45m") == 45
        with pytest.raises(ValueError, match="Invalid time format: 0h"):
            parse_sleep_time("0h")

    def test_parse_sleep_time_minutes_only(self):
        """Test parsing sleep time with minutes only."""
        assert parse_sleep_time("45m") == 45
        with pytest.raises(ValueError, match="Invalid time format: 0m"):
            parse_sleep_time("0m")

    def test_parse_sleep_time_combined(self):
        """Test parsing combined time formats."""
        assert parse_sleep_time("2h15m") == 135
        assert parse_sleep_time("1h5m") == 65

    def test_parse_sleep_time_invalid(self):
        """Test parsing invalid sleep time formats."""
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_sleep_time("2:60")
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_sleep_time("invalid")
        with pytest.raises(ValueError, match="Invalid type"):
            parse_sleep_time(None)

    def test_parse_sleep_time_off(self):
        """Test parsing 'off' for sleep timer."""
        assert parse_sleep_time("off") == 0
        assert parse_sleep_time("OFF") == 0

    def test_parse_sleep_time_range_validation(self):
        """Test sleep timer range validation."""
        assert parse_sleep_time(540) == 540  # Max allowed
        with pytest.raises(ValueError, match="Sleep timer must be between 0 and 540 minutes"):
            parse_sleep_time(541)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.sleep_timer.DysonMQTTClient')
    def test_set_sleep_timer(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting sleep timer."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_sleep_timer(30)
        
        assert result is True
        mock_client.set_numeric_state.assert_called_once_with('sltm', '0030')

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.sleep_timer.DysonMQTTClient')
    def test_set_sleep_timer_zero(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting sleep timer to 0 (off)."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        result = set_sleep_timer(0)
        
        assert result is True
        mock_client.set_numeric_state.assert_called_once_with('sltm', 'OFF')

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.sleep_timer.DysonMQTTClient')
    def test_set_sleep_timer_error(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test sleep timer command error handling."""
        mock_client = Mock()
        mock_client.connect.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client
        
        result = set_sleep_timer(30)
        
        assert result is False


class TestOscillationCommands:
    """Test oscillation control commands."""

    def test_parse_width_input_valid(self):
        """Test parsing valid width inputs."""
        assert parse_width_input("45") == 45
        assert parse_width_input("90") == 90
        assert parse_width_input("180") == 180
        assert parse_width_input("350") == 350
        assert parse_width_input("0") == 0
        assert parse_width_input("off") == 0
        assert parse_width_input("narrow") == 45
        assert parse_width_input("medium") == 90
        assert parse_width_input("wide") == 180
        assert parse_width_input("full") == 350

    def test_parse_width_input_invalid(self):
        """Test parsing invalid width inputs."""
        with pytest.raises(ValueError, match="Invalid width name"):
            parse_width_input("invalid")
        # parse_width_input doesn't validate range, just converts to int
        # But the actual validation happens in set_oscillation_width
        assert parse_width_input("44") == 44
        assert parse_width_input("351") == 351

    def test_get_oscillation_info(self):
        """Test getting oscillation info from angles."""
        info = get_oscillation_info("0135", "0225")
        assert info["width"] == 90
        assert info["heading"] == 180

        info = get_oscillation_info("0180", "0180")
        assert info["width"] == 0
        assert info["heading"] == 180

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_angles_valid(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting valid oscillation angles."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        result = set_oscillation_angles(90, 180)
        
        assert result["success"] is True
        assert result["actual_width"] == 90
        assert result["actual_heading"] == 180
        assert result["lower_angle"] == 135
        assert result["upper_angle"] == 225
        mock_client.send_standalone_command.assert_called_once()

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_angles_zero_width(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test setting oscillation with zero width (heading only)."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        result = set_oscillation_angles(0, 270)
        
        assert result["success"] is True
        assert result["actual_width"] == 0
        assert result["actual_heading"] == 270
        mock_client.send_standalone_command.assert_called_once()

    def test_set_oscillation_angles_invalid_width(self):
        """Test setting oscillation with invalid width."""
        with pytest.raises(ValueError, match="Width must be between 45° and 350°"):
            set_oscillation_angles(44, 180)
        with pytest.raises(ValueError, match="Width must be between 45° and 350°"):
            set_oscillation_angles(351, 180)

    def test_set_oscillation_angles_invalid_heading(self):
        """Test setting oscillation with invalid heading."""
        with pytest.raises(ValueError, match="Heading must be between 0° and 359°"):
            set_oscillation_angles(90, -1)
        with pytest.raises(ValueError, match="Heading must be between 0° and 359°"):
            set_oscillation_angles(90, 360)

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_angles_bounds_adjustment(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test bounds adjustment for oscillation angles."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        # Test that heading gets adjusted when it would cause out-of-bounds angles
        result = set_oscillation_angles(90, 2)  # 2° heading would cause -43° to 47° (invalid)
        
        assert result["success"] is True
        assert result["actual_width"] == 90
        assert result["adjusted"] is True
        assert result["original_heading"] == 2
        # The heading should be adjusted to keep angles within 5°-355° bounds
        assert result["lower_angle"] >= 5
        assert result["upper_angle"] <= 355

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_angles_wrap_around(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test wrap-around case handling."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        # Test wrap-around case (e.g., 350° to 10°)
        result = set_oscillation_angles(180, 0)  # 0° heading with 180° width would cause -90° to 90°
        
        assert result["success"] is True
        assert result["actual_width"] == 180
        assert result["adjusted"] is True
        # The heading should be adjusted to avoid wrap-around
        assert result["lower_angle"] >= 5
        assert result["upper_angle"] <= 355

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_angles_error(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test oscillation command error handling."""
        mock_client = Mock()
        mock_client.send_standalone_command.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client
        
        result = set_oscillation_angles(90, 180)
        
        assert result["success"] is False
        assert "error" in result

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_stop_oscillation(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test stopping oscillation."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        result = stop_oscillation()
        
        assert result is True
        mock_client.send_standalone_command.assert_called_once()

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_stop_oscillation_dict(self, mock_client_class, mock_paho_client, mock_env_vars):
        """Test stopping oscillation with dict return."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        result = stop_oscillation_dict()
        
        assert result["success"] is True
        mock_client.send_standalone_command.assert_called_once()

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_width(self, mock_client_class, mock_async_get_state, mock_paho_client, mock_env_vars):
        """Test setting oscillation width."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        # Mock the async state call to return a fallback
        mock_async_get_state.return_value = None
        
        result = set_oscillation_width("medium")
        
        assert result["success"] is True
        assert result["actual_width"] == 90
        mock_client.send_standalone_command.assert_called_once()

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_width_invalid(self, mock_client_class, mock_async_get_state, mock_paho_client, mock_env_vars):
        """Test setting invalid oscillation width."""
        # Mock the async state call
        mock_async_get_state.return_value = None
        
        result = set_oscillation_width("invalid")
        
        assert result["success"] is False
        assert "error" in result
        assert "Invalid width name" in result["error"]

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_width_adjustment(self, mock_client_class, mock_async_get_state, mock_paho_client, mock_env_vars):
        """Test that invalid widths get adjusted to valid ones."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        # Mock the async state call to return None (fallback to default heading)
        mock_async_get_state.return_value = None
        
        # Test that 44 gets adjusted to 45 (narrow)
        result = set_oscillation_width("44")
        assert result["success"] is True
        assert result["actual_width"] == 45
        assert result["width_adjusted"] is True
        assert result["requested_width"] == "44"
        assert result["adjusted_width"] == "narrow"
        
        # Test that 351 gets adjusted to 350 (full)
        result = set_oscillation_width("351")
        assert result["success"] is True
        assert result["actual_width"] == 350
        assert result["width_adjusted"] is True
        assert result["requested_width"] == "351"
        assert result["adjusted_width"] == "full"

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_width_zero(self, mock_client_class, mock_async_get_state, mock_paho_client, mock_env_vars):
        """Test setting oscillation width to zero (off)."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        # Mock the async state call
        mock_async_get_state.return_value = None
        
        result = set_oscillation_width("off")
        
        assert result["success"] is True
        assert result["actual_width"] == 0
        assert result["adjusted_width"] == "off"

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_direction(self, mock_client_class, mock_async_get_state, mock_paho_client, mock_env_vars):
        """Test setting oscillation direction."""
        mock_client = Mock()
        mock_client.send_standalone_command.return_value = True
        mock_client_class.return_value = mock_client
        
        # Mock the async state call to return None (fallback to default behavior)
        mock_async_get_state.return_value = None
        
        result = set_oscillation_direction(270)
        
        assert result["success"] is True
        assert result["actual_heading"] == 270
        mock_client.send_standalone_command.assert_called_once()

    @patch('paho.mqtt.client.Client')
    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    @patch('dyson2mqtt.commands.oscillation.DysonMQTTClient')
    def test_set_oscillation_direction_invalid(self, mock_client_class, mock_async_get_state, mock_paho_client, mock_env_vars):
        """Test setting invalid oscillation direction."""
        # Mock the async state call
        mock_async_get_state.return_value = None
        
        result = set_oscillation_direction(-1)
        assert result["success"] is False
        assert "Heading must be between 0° and 359°" in result["error"]
        
        result = set_oscillation_direction(360)
        assert result["success"] is False
        assert "Heading must be between 0° and 359°" in result["error"] 