"""
Integration tests for CLI interface.
"""

from io import StringIO
from unittest.mock import patch

import pytest

from blowcontrol.cli import main


class TestCLI:
    """Test CLI interface functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        with patch("sys.argv", ["blowcontrol", "--help"]):
            with patch("argparse.ArgumentParser.print_help") as mock_help:
                # This will raise SystemExit when --help is used
                with pytest.raises(SystemExit):
                    main()
                mock_help.assert_called_once()

    def test_cli_no_command(self):
        """Test CLI with no command specified."""
        with patch("sys.argv", ["blowcontrol"]):
            with pytest.raises(SystemExit):
                main()

    @patch("blowcontrol.cli.set_power")
    def test_cli_power_on(self, mock_set_power):
        """Test CLI power on command."""
        mock_set_power.return_value = True

        with patch("sys.argv", ["blowcontrol", "power", "on"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                assert "Power set to ON" in output
                mock_set_power.assert_called_once_with("on")

    @patch("blowcontrol.cli.set_power")
    def test_cli_power_off(self, mock_set_power):
        """Test CLI power off command."""
        mock_set_power.return_value = True

        with patch("sys.argv", ["blowcontrol", "power", "off"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                assert "Power set to OFF" in output
                mock_set_power.assert_called_once_with("off")

    @patch("blowcontrol.cli.set_fan_speed")
    def test_cli_speed(self, mock_set_speed):
        """Test CLI speed command."""
        mock_set_speed.return_value = True

        with patch("sys.argv", ["blowcontrol", "speed", "5"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                assert "Fan speed set to 5" in output
                mock_set_speed.assert_called_once_with(5)

    @patch("blowcontrol.cli.set_auto_mode")
    def test_cli_auto_on(self, mock_set_auto):
        """Test CLI auto mode on command."""
        mock_set_auto.return_value = True

        with patch("sys.argv", ["blowcontrol", "auto", "on"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                assert "Auto mode set to ON" in output
                mock_set_auto.assert_called_once_with("on")

    @patch("blowcontrol.cli.set_night_mode")
    def test_cli_night_on(self, mock_set_night):
        """Test CLI night mode on command."""
        mock_set_night.return_value = True

        with patch("sys.argv", ["blowcontrol", "night", "on"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                assert "Night mode set to ON" in output
                mock_set_night.assert_called_once_with("on")

    @patch("blowcontrol.cli.set_sleep_timer")
    def test_cli_timer(self, mock_set_timer):
        """Test CLI timer command."""
        mock_set_timer.return_value = True

        with patch("sys.argv", ["blowcontrol", "timer", "30"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                assert "Sleep timer set to 30" in output
                mock_set_timer.assert_called_once_with("30")

    def test_cli_invalid_speed(self):
        """Test CLI with invalid speed."""
        with patch("sys.argv", ["blowcontrol", "speed", "11"]):
            with pytest.raises(SystemExit):
                main()

    def test_cli_invalid_power_state(self):
        """Test CLI with invalid power state."""
        with patch("blowcontrol.commands.power.set_power") as mock_set_power:
            mock_set_power.side_effect = ValueError("Cannot parse 'invalid' as boolean")

            with patch("sys.argv", ["blowcontrol", "power", "invalid"]):
                with pytest.raises(SystemExit):
                    main()

    @patch("blowcontrol.cli.set_power")
    def test_cli_json_output(self, mock_set_power):
        """Test CLI JSON output format."""
        mock_set_power.return_value = True

        with patch("sys.argv", ["blowcontrol", "power", "on", "--json"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert '"success": true' in output
                assert '"message"' in output

    @patch("blowcontrol.cli.set_power")
    def test_cli_error_json_output(self, mock_set_power):
        """Test CLI JSON output format for errors."""
        mock_set_power.return_value = False

        with patch("sys.argv", ["blowcontrol", "power", "on", "--json"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert (
                    '"success": false' in output
                )  # The CLI shows failure when command fails
                assert '"message"' in output

    def test_cli_debug_flag(self):
        """Test CLI debug flag."""
        with patch("sys.argv", ["blowcontrol", "--debug", "--help"]):
            with patch("argparse.ArgumentParser.print_help") as mock_help:
                with pytest.raises(SystemExit):
                    main()
                mock_help.assert_called_once()


class TestCLIState:
    """Test CLI state command specifically."""

    @patch("blowcontrol.mqtt.async_client.async_get_state")
    def test_cli_state(
        self, mock_get_state, sample_device_state, sample_environmental_data
    ):
        """Test CLI state command."""
        mock_get_state.return_value = {
            "state": sample_device_state,
            "environmental": sample_environmental_data,
        }

        with patch("sys.argv", ["blowcontrol", "state"]):
            main()
            mock_get_state.assert_called_once()

    @patch("blowcontrol.mqtt.async_client.async_get_state")
    def test_cli_state_json(
        self, mock_get_state, sample_device_state, sample_environmental_data
    ):
        """Test CLI state command with JSON output."""
        mock_get_state.return_value = {
            "state": sample_device_state,
            "environmental": sample_environmental_data,
        }

        with patch("sys.argv", ["blowcontrol", "state", "--json"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert '"state"' in output
                assert '"environmental"' in output


class TestCLIOscillation:
    """Test CLI oscillation commands."""

    @patch("blowcontrol.cli.set_oscillation_width")
    def test_cli_oscillation_width(self, mock_set_width):
        """Test CLI oscillation width command."""
        mock_set_width.return_value = {"success": True, "actual_width": 90}

        with patch("sys.argv", ["blowcontrol", "width", "medium"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                mock_set_width.assert_called_once_with("medium")

    @patch("blowcontrol.cli.set_oscillation_direction")
    def test_cli_oscillation_heading(self, mock_set_direction):
        """Test CLI oscillation direction command."""
        mock_set_direction.return_value = {"success": True, "actual_heading": 90}

        with patch("sys.argv", ["blowcontrol", "direction", "90"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                mock_set_direction.assert_called_once_with(90)

    @patch("blowcontrol.cli.stop_oscillation_dict")
    def test_cli_oscillation_stop(self, mock_stop):
        """Test CLI oscillation stop command."""
        mock_stop.return_value = {"success": True}

        with patch("sys.argv", ["blowcontrol", "stop"]):
            with patch("sys.stdout", StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "✓" in output
                mock_stop.assert_called_once()
