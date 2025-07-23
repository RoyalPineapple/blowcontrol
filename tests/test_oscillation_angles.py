#!/usr/bin/env python3
"""
Tests for oscillation angle calculations and conversions.
"""

import unittest
from unittest.mock import patch

from dyson2mqtt.commands.oscillation import (
    WIDTH_DISPLAY_NAMES,
    WIDTH_NAMES,
    get_oscillation_info,
    parse_width_input,
    set_oscillation_angles,
)


class TestOscillationAngles(unittest.TestCase):
    """Test oscillation angle calculations and conversions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock client that will be used by all oscillation functions
        self.mock_client_patcher = patch(
            "dyson2mqtt.commands.oscillation.DysonMQTTClient"
        )
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = self.mock_client_class.return_value
        self.mock_client.send_standalone_command.return_value = True

    def tearDown(self):
        """Clean up test fixtures."""
        self.mock_client_patcher.stop()

    def test_width_heading_to_angles(self):
        """Test converting width + heading to lower/upper angles."""
        test_cases = [
            # (width, heading, expected_lower, expected_upper)
            (90, 180, 135, 225),  # Medium width, center
            (45, 90, 68, 112),  # Narrow width, right
            (180, 270, 175, 355),  # Wide width, back (adjusted for bounds)
            (350, 0, 5, 355),  # Full width, front (adjusted for bounds)
            (0, 180, 180, 180),  # Off (no oscillation)
        ]

        for width, heading, expected_lower, expected_upper in test_cases:
            with self.subTest(width=width, heading=heading):
                result = set_oscillation_angles(width, heading)
                self.assertTrue(result["success"])
                self.assertEqual(result["lower_angle"], expected_lower)
                self.assertEqual(result["upper_angle"], expected_upper)
                self.assertEqual(result["actual_width"], width)
                # Heading might be adjusted for bounds, so don't test exact
                # match

    def test_angles_to_width_heading(self):
        """Test converting lower/upper angles back to width + heading."""
        test_cases = [
            # (lower, upper, expected_width, expected_heading)
            (135, 225, 90, 180),  # Medium width, center
            # Narrow width, right (note: 44 not 45 due to rounding)
            (68, 112, 44, 90),
            (175, 355, 180, 265),  # Wide width, back (adjusted)
            (5, 355, 350, 180),  # Full width, front (adjusted)
            (180, 180, 0, 180),  # Off (no oscillation)
        ]

        for lower, upper, expected_width, expected_heading in test_cases:
            with self.subTest(lower=lower, upper=upper):
                result = get_oscillation_info(f"{lower:04d}", f"{upper:04d}")
                self.assertEqual(result["width"], expected_width)
                self.assertEqual(result["heading"], expected_heading)

    def test_bounds_validation(self):
        """Test that angles respect Dyson's 5°-355° bounds."""
        # Test cases that should be adjusted
        test_cases = [
            # (width, heading, expected_adjusted)
            (90, 0, True),  # 0° heading -> -45° to 45° (invalid)
            (90, 2, True),  # 2° heading -> -43° to 47° (invalid)
            (90, 358, True),  # 358° heading -> 313° to 403° (invalid)
            (180, 0, True),  # 0° heading -> -90° to 90° (invalid)
            (350, 180, False),  # 180° heading -> 5° to 355° (valid)
        ]

        for width, heading, should_adjust in test_cases:
            with self.subTest(width=width, heading=heading):
                result = set_oscillation_angles(width, heading)
                self.assertTrue(result["success"])
                self.assertEqual(result["adjusted"], should_adjust)

                # Check bounds are respected
                self.assertGreaterEqual(result["lower_angle"], 5)
                self.assertLessEqual(result["upper_angle"], 355)

    def test_valid_widths(self):
        """Test that valid widths work correctly."""
        valid_widths = [0, 45, 90, 180, 350]

        for width in valid_widths:
            with self.subTest(width=width):
                result = set_oscillation_angles(width, 180)
                self.assertTrue(result["success"])
                self.assertEqual(result["actual_width"], width)

    def test_named_widths(self):
        """Test parsing named width inputs."""
        test_cases = [
            ("off", 0),
            ("narrow", 45),
            ("medium", 90),
            ("wide", 180),
            ("full", 350),
            ("0", 0),
            ("45", 45),
            ("90", 90),
            ("180", 180),
            ("350", 350),
        ]

        for input_name, expected_width in test_cases:
            with self.subTest(input_name=input_name):
                result = parse_width_input(input_name)
                self.assertEqual(result, expected_width)

    def test_invalid_named_widths(self):
        """Test that invalid named widths are rejected."""
        invalid_names = ["invalid", "small", "large"]

        for invalid_name in invalid_names:
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(ValueError):
                    parse_width_input(invalid_name)

    def test_width_names_mapping(self):
        """Test width name mappings are consistent."""
        self.assertEqual(WIDTH_NAMES["off"], 0)
        self.assertEqual(WIDTH_NAMES["narrow"], 45)
        self.assertEqual(WIDTH_NAMES["medium"], 90)
        self.assertEqual(WIDTH_NAMES["wide"], 180)
        self.assertEqual(WIDTH_NAMES["full"], 350)

    def test_width_display_names(self):
        """Test width display names."""
        self.assertEqual(WIDTH_DISPLAY_NAMES[0], "off")
        self.assertEqual(WIDTH_DISPLAY_NAMES[45], "narrow")
        self.assertEqual(WIDTH_DISPLAY_NAMES[90], "medium")
        self.assertEqual(WIDTH_DISPLAY_NAMES[180], "wide")
        self.assertEqual(WIDTH_DISPLAY_NAMES[350], "full")

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test minimum valid heading (gets adjusted)
        result = set_oscillation_angles(45, 5)
        self.assertTrue(result["success"])
        self.assertEqual(result["lower_angle"], 5)
        self.assertEqual(result["upper_angle"], 49)
        self.assertTrue(result["adjusted"])

        # Test maximum valid heading (gets adjusted)
        result = set_oscillation_angles(45, 355)
        self.assertTrue(result["success"])
        self.assertEqual(result["lower_angle"], 311)
        self.assertEqual(result["upper_angle"], 355)
        self.assertTrue(result["adjusted"])

        # Test zero width (off)
        result = set_oscillation_angles(0, 180)
        self.assertTrue(result["success"])
        self.assertEqual(result["lower_angle"], 180)
        self.assertEqual(result["upper_angle"], 180)

    def test_round_trip_conversion(self):
        """Test that converting width+heading to angles and back gives same result."""
        test_cases = [
            (45, 90),
            (90, 180),
            (180, 270),
            (350, 0),
        ]

        for width, heading in test_cases:
            with self.subTest(width=width, heading=heading):
                # Convert to angles
                result = set_oscillation_angles(width, heading)
                self.assertTrue(result["success"])

                lower = result["lower_angle"]
                upper = result["upper_angle"]

                # Convert back to width + heading
                info = get_oscillation_info(f"{lower:04d}", f"{upper:04d}")

                # Width should be close (within 1° due to integer division)
                width_diff = abs(info["width"] - result["actual_width"])
                self.assertLessEqual(
                    width_diff,
                    1,
                    f"Width difference too large: {info['width']} vs {result['actual_width']}",
                )

                # Heading should be close (within 1° due to integer division)
                heading_diff = abs(info["heading"] - result["actual_heading"])
                self.assertLessEqual(
                    heading_diff,
                    1,
                    f"Heading difference too large: {info['heading']} vs {result['actual_heading']}",
                )

    def test_smart_adjustment_logic(self):
        """Test that heading adjustments prefer width preservation."""
        # Test case where width would be preserved
        result = set_oscillation_angles(90, 0)  # Would be -45° to 45°
        self.assertTrue(result["success"])
        self.assertTrue(result["adjusted"])
        self.assertEqual(result["actual_width"], 90)  # Width preserved
        self.assertNotEqual(result["actual_heading"], 0)  # Heading adjusted

        # Verify the adjusted heading puts angles within bounds
        self.assertGreaterEqual(result["lower_angle"], 5)
        self.assertLessEqual(result["upper_angle"], 355)

    def test_wrap_around_detection(self):
        """Test wrap-around angle detection."""
        # Test normal case (no wrap-around)
        result = get_oscillation_info("0135", "0225")
        self.assertFalse(result["is_wrap_around"])

        # Test wrap-around case (would need to be within bounds)
        # Note: Our implementation doesn't allow wrap-around in normal cases
        # but the detection logic exists


if __name__ == "__main__":
    unittest.main(verbosity=2)
