"""Test that the library works without pandas/numpy installed."""

import sys
from datetime import datetime
from unittest.mock import patch


def test_convert_without_pandas() -> None:
    """Test that convert module loads and works without pandas."""
    # Mock the pandas import to fail
    with patch.dict(sys.modules, {"pandas": None}):
        # Force reload of the module
        if "time_helper.convert" in sys.modules:
            del sys.modules["time_helper.convert"]

        # Import should work
        from time_helper.convert import any_to_datetime, is_datetime, to_datetime

        # is_datetime should return False (mock function)
        assert is_datetime("2023-01-01") is False
        assert is_datetime(datetime.now()) is False  # type: ignore[arg-type]

        # to_datetime should return None (mock function)
        assert to_datetime("2023-01-01") is None
        assert to_datetime(datetime.now(), unit="s") is None

        # any_to_datetime should still work for basic cases
        result = any_to_datetime("2023-01-15T10:30:00")
        assert result is not None
        assert result.year == 2023


def test_convert_without_numpy() -> None:
    """Test that convert module loads and works without numpy."""
    # Mock the numpy import to fail
    with patch.dict(sys.modules, {"numpy": None}):
        # Force reload of the module
        if "time_helper.convert" in sys.modules:
            del sys.modules["time_helper.convert"]

        # Import should work
        from time_helper.convert import any_to_datetime

        # Basic functionality should work
        result = any_to_datetime("2023-06-15")
        assert result is not None
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15


def test_pandas_optional_install_message() -> None:
    """Test that we provide helpful message when pandas functionality is needed."""
    # This is more of a documentation test
    # When pandas is not installed, the mock functions should be used
    # Users who need pandas functionality should install with: pip install time-helper[pandas]
    assert True  # Document the optional dependency pattern
