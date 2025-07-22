#!/usr/bin/env python3
"""
Tests for device state management and printing.
"""

import pytest
from unittest.mock import patch, MagicMock
from dyson2mqtt.state.device_state import DeviceStatePrinter


class TestDeviceStatePrinter:
    """Test device state printing functionality."""

    def test_print_current_state_power_on(self):
        """Test printing current state with power on."""
        state_data = {
            'fpwr': ['ON', 'ON'],
            'fnsp': ['AUTO', '5'],
            'auto': ['ON', 'ON'],
            'nmod': ['OFF', 'OFF'],
            'oson': ['ON', 'ON'],
            'osal': ['0090', '0090'],
            'osau': ['0270', '0270'],
            'sltm': ['OFF', 'OFF']
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_current_state(state_data)
            
            # Check that print was called
            assert mock_print.called
            # Check that power status was printed
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('Power: ON' in str(call) for call in calls)

    def test_print_current_state_power_off(self):
        """Test printing current state with power off."""
        state_data = {
            'fpwr': ['OFF', 'OFF'],
            'fnsp': ['AUTO', '0'],
            'auto': ['OFF', 'OFF'],
            'nmod': ['OFF', 'OFF'],
            'oson': ['OFF', 'OFF'],
            'osal': ['0000', '0000'],
            'osau': ['0000', '0000'],
            'sltm': ['OFF', 'OFF']
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_current_state(state_data)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('Power: OFF' in str(call) for call in calls)

    def test_print_current_state_with_oscillation(self):
        """Test printing current state with oscillation enabled."""
        state_data = {
            'fpwr': ['ON', 'ON'],
            'fnsp': ['AUTO', '3'],
            'auto': ['OFF', 'OFF'],
            'nmod': ['OFF', 'OFF'],
            'oson': ['ON', 'ON'],
            'osal': ['0090', '0090'],
            'osau': ['0270', '0270'],
            'sltm': ['OFF', 'OFF']
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_current_state(state_data)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('Oscillation: ON' in str(call) for call in calls)
            assert any('Width: 180°' in str(call) for call in calls)
            assert any('Heading: 180°' in str(call) for call in calls)

    def test_print_current_state_with_sleep_timer(self):
        """Test printing current state with sleep timer."""
        state_data = {
            'fpwr': ['ON', 'ON'],
            'fnsp': ['AUTO', '2'],
            'auto': ['OFF', 'OFF'],
            'nmod': ['OFF', 'OFF'],
            'oson': ['OFF', 'OFF'],
            'osal': ['0000', '0000'],
            'osau': ['0000', '0000'],
            'sltm': ['ON', '30']
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_current_state(state_data)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('Sleep Timer: 30' in str(call) for call in calls)

    def test_print_environmental_data(self):
        """Test printing environmental data."""
        env_data = {
            'data': [
                {
                    'hact': '0001',
                    'pm25': '0002',
                    'pm10': '0003',
                    'va10': '0004',
                    'noxl': '0005',
                    'p25r': '0006',
                    'p10r': '0007',
                    'sltm': 'OFF'
                }
            ]
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_environmental(env_data)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('Humidity: 1%' in str(call) for call in calls)
            assert any('PM2.5: 2' in str(call) for call in calls)
            assert any('PM10: 3' in str(call) for call in calls)

    def test_print_environmental_data_empty(self):
        """Test printing empty environmental data."""
        env_data = {'data': []}
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_environmental(env_data)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('No environmental data' in str(call) for call in calls)

    def test_print_environmental_data_missing_fields(self):
        """Test printing environmental data with missing fields."""
        env_data = {
            'data': [
                {
                    'hact': '0001',
                    # Missing other fields
                }
            ]
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_environmental(env_data)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('Humidity: 1%' in str(call) for call in calls)

    def test_print_current_state_missing_fields(self):
        """Test printing current state with missing fields."""
        state_data = {
            'fpwr': ['ON', 'ON'],
            # Missing other fields
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_current_state(state_data)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any('Power: ON' in str(call) for call in calls)

    def test_print_current_state_empty(self):
        """Test printing empty current state."""
        state_data = {}
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_current_state(state_data)
            
            # Should handle empty state gracefully
            assert mock_print.called


class TestDeviceStateFunctions:
    """Test device state functions."""

    def test_print_current_state_function(self):
        """Test print_current_state function."""
        state_data = {
            'product-state': {
                'fpwr': ['ON', 'ON'],
                'fnsp': ['AUTO', '5']
            }
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_current_state(state_data)
            assert mock_print.called

    def test_print_environmental_function(self):
        """Test print_environmental function."""
        env_data = {
            'data': [
                {
                    'hact': '0001',
                    'pm25': '0002'
                }
            ]
        }
        
        with patch('builtins.print') as mock_print:
            DeviceStatePrinter.print_environmental(env_data)
            assert mock_print.called 