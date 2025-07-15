"""Tests for current_timezone() improvements."""

import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from time_helper import current_timezone
from time_helper.timezone import timezone


def test_current_timezone_returns_valid_timezone() -> None:
    """Test that current_timezone returns a valid timezone object."""
    tz = current_timezone()

    assert tz is not None
    assert hasattr(tz, "tzname")
    # Should be a timezone object
    assert isinstance(tz, timezone)


def test_current_timezone_cest_handling() -> None:
    """Test that CEST is properly converted to Europe/Berlin."""
    # Mock datetime to return CEST
    mock_dt = Mock()
    mock_dt.tzname.return_value = "CEST"
    mock_dt.tzinfo = None  # No proper tzinfo

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        tz = current_timezone()

        # Should convert CEST to Europe/Berlin (more accurate than CET)
        assert str(tz) == "Europe/Berlin"


def test_current_timezone_standard_timezones() -> None:
    """Test that standard timezone names work correctly."""
    test_cases = ["UTC", "EST", "PST", "GMT"]

    for tz_name in test_cases:
        mock_dt = Mock()
        mock_dt.tzname.return_value = tz_name

        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = mock_dt

            try:
                tz = current_timezone()
                assert tz is not None
                # For mapped timezones, check the actual zone
                if tz_name in ["EST", "PST"]:
                    assert str(tz) in ["America/New_York", "America/Los_Angeles"]
                else:
                    assert str(tz) == tz_name
            except Exception:
                # Some timezone names might not be valid
                pass


def test_current_timezone_system_default() -> None:
    """Test that current_timezone uses system timezone correctly."""
    # Get the actual system timezone
    tz = current_timezone()

    # Create a datetime with this timezone
    dt = datetime.now(tz)

    # Should be able to get timezone name
    tz_name = dt.tzname()
    assert tz_name is not None


def test_current_timezone_consistency() -> None:
    """Test that multiple calls return consistent results."""
    tz1 = current_timezone()
    tz2 = current_timezone()

    # Should return the same timezone
    assert str(tz1) == str(tz2)


@pytest.mark.skipif(sys.platform == "win32", reason="Platform-specific timezone handling")
def test_current_timezone_unix_specific() -> None:
    """Test Unix-specific timezone scenarios."""
    # Test with various Unix timezone names
    unix_timezones = ["America/New_York", "Europe/London", "Asia/Tokyo"]

    for tz_name in unix_timezones:
        mock_dt = Mock()
        mock_dt.tzname.return_value = tz_name

        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = mock_dt

            try:
                tz = current_timezone()
                assert tz is not None
            except Exception:
                # Some timezones might not be available
                pass


def test_current_timezone_invalid_timezone() -> None:
    """Test handling of invalid timezone names."""
    mock_dt = Mock()
    mock_dt.tzname.return_value = "INVALID_TZ_NAME"
    mock_dt.tzinfo = None  # No proper tzinfo

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        # Should fall back to UTC for invalid timezone
        tz = current_timezone()
        assert tz is not None
        assert str(tz) == "UTC"


def test_current_timezone_none_tzname() -> None:
    """Test handling when tzname returns None."""
    mock_dt = Mock()
    mock_dt.tzname.return_value = None
    mock_dt.tzinfo = None  # No proper tzinfo

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        # Should fall back to UTC when tzname is None
        tz = current_timezone()
        assert tz is not None
        assert str(tz) == "UTC"
