#!/usr/bin/env python3
"""
Tests for entry point modules.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestEntryPoints:
    """Test entry point modules."""

    @patch('dyson2mqtt.cli.main')
    def test_main_entry_point(self, mock_main):
        """Test main.py entry point."""
        with patch('sys.argv', ['dyson2mqtt']):
            import dyson2mqtt.main
            mock_main.assert_called_once()

    @patch('dyson2mqtt.cli.main')
    def test_module_entry_point(self, mock_main):
        """Test __main__.py entry point."""
        with patch('sys.argv', ['dyson2mqtt']):
            import dyson2mqtt.__main__
            mock_main.assert_called_once() 