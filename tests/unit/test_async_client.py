#!/usr/bin/env python3
"""
Tests for async MQTT client functionality.
"""

from unittest.mock import patch

import pytest

from dyson2mqtt.mqtt.async_client import (
    async_get_state,
    async_set_fan_speed,
    async_set_power,
)


class TestAsyncClient:
    """Test async MQTT client functions."""

    @pytest.mark.asyncio
    @patch('dyson2mqtt.mqtt.async_client.DysonMQTTClient')
    async def test_async_get_state_success(self, mock_client_class):
        """Test successful async state retrieval."""
        with patch('dyson2mqtt.mqtt.async_client.asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = {
                'state': {'product-state': {'fpwr': ['ON', 'ON']}},
                'environmental': {'data': [{'hact': '0001', 'pm25': '0002'}]}
            }

            result = await async_get_state()

            assert 'state' in result
            assert 'environmental' in result
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    @patch('dyson2mqtt.mqtt.async_client.DysonMQTTClient')
    async def test_async_get_state_failure(self, mock_client_class):
        """Test async state retrieval failure."""
        with patch('dyson2mqtt.mqtt.async_client.asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = {
                'state': None, 'environmental': None}

            result = await async_get_state()

            assert 'state' in result
            assert 'environmental' in result
            assert result['state'] is None
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    @patch('dyson2mqtt.mqtt.async_client.DysonMQTTClient')
    async def test_async_set_power_on(self, mock_client_class):
        """Test async power on."""
        with patch('dyson2mqtt.mqtt.async_client.asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = True
            result = await async_set_power(True)
            assert result is True
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    @patch('dyson2mqtt.mqtt.async_client.DysonMQTTClient')
    async def test_async_set_power_off(self, mock_client_class):
        """Test async power off."""
        with patch('dyson2mqtt.mqtt.async_client.asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = True
            result = await async_set_power(False)
            assert result is True
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    @patch('dyson2mqtt.mqtt.async_client.DysonMQTTClient')
    async def test_async_set_fan_speed(self, mock_client_class):
        """Test async fan speed setting."""
        with patch('dyson2mqtt.mqtt.async_client.asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = True
            result = await async_set_fan_speed(5)
            assert result is True
            mock_to_thread.assert_called_once()
