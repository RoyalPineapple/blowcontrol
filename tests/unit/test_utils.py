"""
Unit tests for utility functions.
"""

import pytest
from dyson2mqtt.utils import parse_boolean


class TestParseBoolean:
    """Test flexible boolean parsing utility."""

    def test_boolean_inputs(self):
        """Test boolean inputs."""
        assert parse_boolean(True) is True
        assert parse_boolean(False) is False

    def test_string_true_values(self):
        """Test string true values."""
        assert parse_boolean("true") is True
        assert parse_boolean("TRUE") is True
        assert parse_boolean("True") is True
        assert parse_boolean("t") is True
        assert parse_boolean("T") is True
        assert parse_boolean("1") is True
        assert parse_boolean("on") is True
        assert parse_boolean("ON") is True
        assert parse_boolean("On") is True
        assert parse_boolean("yes") is True
        assert parse_boolean("YES") is True
        assert parse_boolean("Yes") is True
        assert parse_boolean("y") is True
        assert parse_boolean("Y") is True

    def test_string_false_values(self):
        """Test string false values."""
        assert parse_boolean("false") is False
        assert parse_boolean("FALSE") is False
        assert parse_boolean("False") is False
        assert parse_boolean("f") is False
        assert parse_boolean("F") is False
        assert parse_boolean("0") is False
        assert parse_boolean("off") is False
        assert parse_boolean("OFF") is False
        assert parse_boolean("Off") is False
        assert parse_boolean("no") is False
        assert parse_boolean("NO") is False
        assert parse_boolean("No") is False
        assert parse_boolean("n") is False
        assert parse_boolean("N") is False

    def test_integer_inputs(self):
        """Test integer inputs."""
        assert parse_boolean(1) is True
        assert parse_boolean(0) is False

    def test_whitespace_handling(self):
        """Test whitespace handling."""
        assert parse_boolean("  true  ") is True
        assert parse_boolean("  false  ") is False
        assert parse_boolean("  t  ") is True
        assert parse_boolean("  f  ") is False
        assert parse_boolean("  1  ") is True
        assert parse_boolean("  0  ") is False

    def test_invalid_inputs(self):
        """Test invalid inputs raise ValueError."""
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean("invalid")
        
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean("maybe")
        
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean("2")
        
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean(-1)
        
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean(None)
        
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean(1.5)
        
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean([])
        
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean({})

    def test_edge_cases(self):
        """Test edge cases."""
        # Empty string
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean("")
        
        # Just whitespace
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_boolean("   ")
        
        # Mixed case variations
        assert parse_boolean("TrUe") is True
        assert parse_boolean("FaLsE") is False
        assert parse_boolean("On") is True
        assert parse_boolean("OfF") is False 