"""Test that unix_to_datetime logging works correctly."""

import logging

import pytest

from time_helper.convert import unix_to_datetime


def test_unix_to_datetime_without_timezone_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Test that unix_to_datetime logs warning when no timezone is provided."""
    caplog.clear()

    # Unix timestamp for 2009-02-13 23:31:30 UTC
    timestamp = 1234567890

    with caplog.at_level(logging.WARNING):
        result = unix_to_datetime(timestamp)

    # Should parse correctly
    assert result is not None
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13

    # Should have logged a warning
    assert len(caplog.records) > 0
    warning_found = False
    for record in caplog.records:
        if record.levelname == "WARNING" and "timezone" in record.message:
            warning_found = True
            assert "inferring 'UTC' as default" in record.message
            break
    assert warning_found, "Expected warning about missing timezone not found"


def test_unix_to_datetime_with_timezone_no_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Test that unix_to_datetime doesn't log warning when timezone is provided."""
    caplog.clear()

    timestamp = 1234567890

    with caplog.at_level(logging.WARNING):
        result = unix_to_datetime(timestamp, tz="America/New_York")

    # Should parse correctly
    assert result is not None

    # Should NOT have logged a warning about timezone
    warning_records = [r for r in caplog.records if r.levelname == "WARNING" and "timezone" in r.message]
    assert len(warning_records) == 0
