"""
Integration tests for CLI interface.
"""

import pytest
import subprocess
import sys
from unittest.mock import patch, Mock
from io import StringIO


class TestCLI:
    """Test CLI interface functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Dyson2MQTT Command Line Controller' in result.stdout
        assert 'power' in result.stdout
        assert 'speed' in result.stdout
        assert 'state' in result.stdout

    def test_cli_no_command(self):
        """Test CLI with no command specified."""
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt'
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert 'error' in result.stderr.lower() or 'required' in result.stderr.lower()

    @patch('dyson2mqtt.commands.power.set_power')
    def test_cli_power_on(self, mock_set_power):
        """Test CLI power on command."""
        mock_set_power.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'power', 'on'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '✓' in result.stdout
        mock_set_power.assert_called_once_with(True)

    @patch('dyson2mqtt.commands.power.set_power')
    def test_cli_power_off(self, mock_set_power):
        """Test CLI power off command."""
        mock_set_power.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'power', 'off'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '✓' in result.stdout
        mock_set_power.assert_called_once_with(False)

    @patch('dyson2mqtt.commands.fan_speed.set_fan_speed')
    def test_cli_speed(self, mock_set_speed):
        """Test CLI speed command."""
        mock_set_speed.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'speed', '5'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '✓' in result.stdout
        mock_set_speed.assert_called_once_with(5)

    @patch('dyson2mqtt.commands.auto_mode.set_auto_mode')
    def test_cli_auto_on(self, mock_set_auto):
        """Test CLI auto mode on command."""
        mock_set_auto.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'auto', 'on'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '✓' in result.stdout
        mock_set_auto.assert_called_once_with(True)

    @patch('dyson2mqtt.commands.night_mode.set_night_mode')
    def test_cli_night_on(self, mock_set_night):
        """Test CLI night mode on command."""
        mock_set_night.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'night', 'on'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '✓' in result.stdout
        mock_set_night.assert_called_once_with(True)

    @patch('dyson2mqtt.commands.sleep_timer.set_sleep_timer')
    def test_cli_timer(self, mock_set_timer):
        """Test CLI timer command."""
        mock_set_timer.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'timer', '30'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '✓' in result.stdout
        mock_set_timer.assert_called_once_with('30')

    def test_cli_invalid_speed(self):
        """Test CLI with invalid speed."""
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'speed', '11'
        ], capture_output=True, text=True)
        
        assert result.returncode != 0

    def test_cli_invalid_power_state(self):
        """Test CLI with invalid power state."""
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'power', 'invalid'
        ], capture_output=True, text=True)
        
        assert result.returncode != 0

    @patch('dyson2mqtt.commands.power.set_power')
    def test_cli_json_output(self, mock_set_power):
        """Test CLI JSON output format."""
        mock_set_power.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'power', 'on', '--json'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '"success": true' in result.stdout
        assert '"message"' in result.stdout

    @patch('dyson2mqtt.commands.power.set_power')
    def test_cli_error_json_output(self, mock_set_power):
        """Test CLI JSON output format for errors."""
        mock_set_power.return_value = False
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'power', 'on', '--json'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '"success": false' in result.stdout

    def test_cli_debug_flag(self):
        """Test CLI debug flag."""
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', '--debug', '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Dyson2MQTT Command Line Controller' in result.stdout


class TestCLIState:
    """Test CLI state command specifically."""

    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    def test_cli_state(self, mock_get_state, sample_device_state, sample_environmental_data):
        """Test CLI state command."""
        mock_get_state.return_value = {
            'state': sample_device_state,
            'environmental': sample_environmental_data
        }
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'state'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'DYSON DEVICE STATE' in result.stdout
        assert 'Fan Power' in result.stdout

    @patch('dyson2mqtt.mqtt.async_client.async_get_state')
    def test_cli_state_json(self, mock_get_state, sample_device_state, sample_environmental_data):
        """Test CLI state command with JSON output."""
        mock_get_state.return_value = {
            'state': sample_device_state,
            'environmental': sample_environmental_data
        }
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'state', '--json'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '"state"' in result.stdout
        assert '"environmental"' in result.stdout


class TestCLIOscillation:
    """Test CLI oscillation commands."""

    @patch('dyson2mqtt.commands.oscillation.set_oscillation_width')
    def test_cli_oscillation_width(self, mock_set_width):
        """Test CLI oscillation width command."""
        mock_set_width.return_value = {'success': True}
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'oscillation', 'width', 'medium'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        mock_set_width.assert_called_once_with('medium', 180)

    @patch('dyson2mqtt.commands.oscillation.set_oscillation_heading')
    def test_cli_oscillation_heading(self, mock_set_heading):
        """Test CLI oscillation heading command."""
        mock_set_heading.return_value = {'success': True}
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'oscillation', 'heading', '90'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        mock_set_heading.assert_called_once_with(90)

    @patch('dyson2mqtt.commands.oscillation.set_oscillation_preset')
    def test_cli_oscillation_preset(self, mock_set_preset):
        """Test CLI oscillation preset command."""
        mock_set_preset.return_value = {'success': True}
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'oscillation', 'preset', 'wide'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        mock_set_preset.assert_called_once_with('wide')

    @patch('dyson2mqtt.commands.oscillation.stop_oscillation')
    def test_cli_oscillation_stop(self, mock_stop):
        """Test CLI oscillation stop command."""
        mock_stop.return_value = True
        
        result = subprocess.run([
            sys.executable, '-m', 'dyson2mqtt', 'oscillation', 'stop'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        mock_stop.assert_called_once() 