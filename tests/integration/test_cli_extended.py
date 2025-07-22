#!/usr/bin/env python3
"""
Extended CLI tests to improve coverage.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO
from dyson2mqtt.cli import main, output_result


class TestCLIExtended:
    """Extended CLI tests for better coverage."""

    def test_output_result_success_json(self):
        """Test output_result with success and JSON mode."""
        with patch('builtins.print') as mock_print:
            output_result(True, "Test message", {"data": "value"}, json_mode=True)
            mock_print.assert_called_once()
            output = mock_print.call_args[0][0]
            assert '"success": true' in output
            assert '"message": "Test message"' in output
            assert '"data": "value"' in output

    def test_output_result_failure_json(self):
        """Test output_result with failure and JSON mode."""
        with patch('builtins.print') as mock_print:
            output_result(False, "Error message", {"error": "details"}, json_mode=True)
            mock_print.assert_called_once()
            output = mock_print.call_args[0][0]
            assert '"success": false' in output
            assert '"message": "Error message"' in output
            assert '"error": "details"' in output

    def test_output_result_success_plain(self):
        """Test output_result with success and plain mode."""
        with patch('builtins.print') as mock_print:
            output_result(True, "Success message")
            mock_print.assert_called_once_with("✓ Success message")

    def test_output_result_failure_plain(self):
        """Test output_result with failure and plain mode."""
        with patch('builtins.print') as mock_print:
            output_result(False, "Error message")
            mock_print.assert_called_once_with("✗ Error message")

    def test_output_result_with_data(self):
        """Test output_result with additional data."""
        with patch('builtins.print') as mock_print:
            output_result(True, "Test message", {"key": "value"})
            mock_print.assert_called_once_with("✓ Test message")

    @patch('dyson2mqtt.cli.set_power')
    def test_cli_power_invalid_state(self, mock_set_power):
        """Test CLI power command with invalid state."""
        with patch('sys.argv', ['dyson2mqtt', 'power', 'invalid']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Invalid power state' in output

    @patch('dyson2mqtt.cli.set_auto_mode')
    def test_cli_auto_invalid_state(self, mock_set_auto):
        """Test CLI auto command with invalid state."""
        with patch('sys.argv', ['dyson2mqtt', 'auto', 'invalid']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Invalid auto mode state' in output

    @patch('dyson2mqtt.cli.set_night_mode')
    def test_cli_night_invalid_state(self, mock_set_night):
        """Test CLI night command with invalid state."""
        with patch('sys.argv', ['dyson2mqtt', 'night', 'invalid']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Invalid night mode state' in output

    @patch('dyson2mqtt.cli.set_fan_speed')
    def test_cli_speed_invalid_range(self, mock_set_speed):
        """Test CLI speed command with invalid range."""
        with patch('sys.argv', ['dyson2mqtt', 'speed', '15']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Invalid fan speed' in output

    @patch('dyson2mqtt.cli.set_sleep_timer')
    def test_cli_timer_invalid_value(self, mock_set_timer):
        """Test CLI timer command with invalid value."""
        with patch('sys.argv', ['dyson2mqtt', 'timer', 'invalid']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Invalid timer value' in output

    @patch('dyson2mqtt.cli.set_power')
    def test_cli_power_exception(self, mock_set_power):
        """Test CLI power command with exception."""
        mock_set_power.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'power', 'on']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to set power' in output

    @patch('dyson2mqtt.cli.set_auto_mode')
    def test_cli_auto_exception(self, mock_set_auto):
        """Test CLI auto command with exception."""
        mock_set_auto.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'auto', 'on']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to set auto mode' in output

    @patch('dyson2mqtt.cli.set_night_mode')
    def test_cli_night_exception(self, mock_set_night):
        """Test CLI night command with exception."""
        mock_set_night.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'night', 'on']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to set night mode' in output

    @patch('dyson2mqtt.cli.set_fan_speed')
    def test_cli_speed_exception(self, mock_set_speed):
        """Test CLI speed command with exception."""
        mock_set_speed.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'speed', '5']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to set fan speed' in output

    @patch('dyson2mqtt.cli.set_sleep_timer')
    def test_cli_timer_exception(self, mock_set_timer):
        """Test CLI timer command with exception."""
        mock_set_timer.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'timer', '30']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to set sleep timer' in output

    @patch('dyson2mqtt.cli.DysonMQTTClient')
    def test_cli_listen_exception(self, mock_client_class):
        """Test CLI listen command with exception."""
        mock_client = mock_client_class.return_value
        mock_client.connect.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'listen']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to start listening' in output

    @patch('dyson2mqtt.cli.async_get_state')
    def test_cli_state_exception(self, mock_get_state):
        """Test CLI state command with exception."""
        mock_get_state.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'state']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to get state' in output

    @patch('dyson2mqtt.cli.set_oscillation_width')
    def test_cli_width_exception(self, mock_set_width):
        """Test CLI width command with exception."""
        mock_set_width.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'width', 'medium']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to set oscillation width' in output

    @patch('dyson2mqtt.cli.set_oscillation_direction')
    def test_cli_direction_exception(self, mock_set_direction):
        """Test CLI direction command with exception."""
        mock_set_direction.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'direction', '180']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to set oscillation direction' in output

    @patch('dyson2mqtt.cli.stop_oscillation')
    def test_cli_stop_exception(self, mock_stop):
        """Test CLI stop command with exception."""
        mock_stop.side_effect = Exception("Connection failed")
        with patch('sys.argv', ['dyson2mqtt', 'stop']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stdout.getvalue()
                assert 'Failed to stop oscillation' in output

    def test_cli_unknown_command(self):
        """Test CLI with unknown command."""
        with patch('sys.argv', ['dyson2mqtt', 'unknown']):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with pytest.raises(SystemExit):
                    main()
                # Should show help or error message
                assert mock_stdout.getvalue() != ""

    def test_cli_debug_logging(self):
        """Test CLI debug flag enables logging."""
        with patch('sys.argv', ['dyson2mqtt', '--debug', '--help']):
            with patch('logging.basicConfig') as mock_logging:
                with patch('argparse.ArgumentParser.print_help'):
                    with pytest.raises(SystemExit):
                        main()
                mock_logging.assert_called_with(level='INFO') 