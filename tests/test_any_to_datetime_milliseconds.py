"""Tests for any_to_datetime millisecond handling - Issue #9."""

from datetime import datetime

from time_helper import any_to_datetime, parse_time


def test_any_to_datetime_with_milliseconds() -> None:
    """Test that any_to_datetime correctly handles datetime strings with milliseconds.

    This tests the fix for Issue #9.
    """
    # Test various millisecond formats
    test_cases = [
        # ISO 8601 with milliseconds and Z
        ("2022-10-15T04:53:30.315Z", datetime(2022, 10, 15, 4, 53, 30, 315000)),
        # ISO 8601 with microseconds
        ("2022-10-15T04:53:30.315123Z", datetime(2022, 10, 15, 4, 53, 30, 315123)),
        # Without Z
        ("2022-10-15T04:53:30.315", datetime(2022, 10, 15, 4, 53, 30, 315000)),
        # With timezone offset
        ("2022-10-15T04:53:30.315+00:00", datetime(2022, 10, 15, 4, 53, 30, 315000)),
        # Space separator
        ("2022-10-15 04:53:30.315", datetime(2022, 10, 15, 4, 53, 30, 315000)),
        # Different millisecond precisions
        ("2022-10-15T04:53:30.3", datetime(2022, 10, 15, 4, 53, 30, 300000)),
        ("2022-10-15T04:53:30.31", datetime(2022, 10, 15, 4, 53, 30, 310000)),
        ("2022-10-15T04:53:30.315", datetime(2022, 10, 15, 4, 53, 30, 315000)),
        ("2022-10-15T04:53:30.3156", datetime(2022, 10, 15, 4, 53, 30, 315600)),
        ("2022-10-15T04:53:30.31567", datetime(2022, 10, 15, 4, 53, 30, 315670)),
        ("2022-10-15T04:53:30.315678", datetime(2022, 10, 15, 4, 53, 30, 315678)),
    ]

    for input_str, expected in test_cases:
        result = any_to_datetime(input_str)
        assert result is not None, f"Failed to parse {input_str}"
        # Compare without timezone info for simplicity
        if result.tzinfo:
            result = result.replace(tzinfo=None)
        assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"


def test_any_to_datetime_milliseconds_vs_parse_time() -> None:
    """Test that any_to_datetime handles milliseconds as well as parse_time."""
    test_string = "2022-10-15T04:53:30.315Z"

    # Test with parse_time (which should work according to issue)
    format_str = "%Y-%m-%dT%H:%M:%S.%fZ"
    parse_result = parse_time(test_string, format_str, "UTC")

    # Test with any_to_datetime (which should also work after fix)
    any_result = any_to_datetime(test_string)

    assert any_result is not None, "any_to_datetime should parse millisecond strings"
    assert parse_result is not None, "parse_time should parse millisecond strings"

    # Compare the results (ignoring timezone for simplicity)
    parse_result_naive = parse_result.replace(tzinfo=None)
    any_result_naive = any_result.replace(tzinfo=None) if any_result.tzinfo else any_result

    assert any_result_naive == parse_result_naive, "any_to_datetime should produce same result as parse_time"


def test_any_to_datetime_edge_cases() -> None:
    """Test edge cases for millisecond parsing."""
    # Test with various edge cases
    test_cases = [
        # No milliseconds
        ("2022-10-15T04:53:30", datetime(2022, 10, 15, 4, 53, 30)),
        # Zero milliseconds
        ("2022-10-15T04:53:30.000", datetime(2022, 10, 15, 4, 53, 30, 0)),
        # Maximum microseconds
        ("2022-10-15T04:53:30.999999", datetime(2022, 10, 15, 4, 53, 30, 999999)),
        # With date only (no milliseconds expected)
        ("2022-10-15", datetime(2022, 10, 15, 0, 0, 0)),
    ]

    for input_str, expected in test_cases:
        result = any_to_datetime(input_str)
        assert result is not None, f"Failed to parse {input_str}"
        if result.tzinfo:
            result = result.replace(tzinfo=None)
        assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"


def test_any_to_datetime_preserves_timezone_with_milliseconds() -> None:
    """Test that timezone information is preserved when parsing milliseconds."""
    # ISO format with Z (UTC)
    result = any_to_datetime("2022-10-15T04:53:30.315Z")
    assert result is not None
    assert result.tzinfo is not None
    # The Z should be parsed as UTC

    # With explicit timezone offset
    result = any_to_datetime("2022-10-15T04:53:30.315+02:00")
    assert result is not None
    assert result.tzinfo is not None


def test_any_to_datetime_with_custom_format() -> None:
    """Test that custom date format parameter works with milliseconds."""
    # Custom format with milliseconds
    custom_format = "%d/%m/%Y %H:%M:%S.%f"
    test_string = "15/10/2022 04:53:30.315"

    result = any_to_datetime(test_string, date_format=custom_format)
    assert result is not None
    assert result == datetime(2022, 10, 15, 4, 53, 30, 315000)


def test_any_to_datetime_invalid_milliseconds() -> None:
    """Test that invalid millisecond formats are handled gracefully."""
    # These should either parse without milliseconds or return None
    invalid_cases = [
        "2022-10-15T04:53:30.",  # Trailing dot
        "2022-10-15T04:53:30.abc",  # Non-numeric milliseconds
    ]

    for test_str in invalid_cases:
        # Should not raise exception
        try:
            result = any_to_datetime(test_str)
            # If it returns something, it should be a valid datetime
            if result is not None:
                assert isinstance(result, datetime)
        except ValueError:
            # ValueError is acceptable for truly invalid formats
            pass


def test_any_to_datetime_z_suffix_formats() -> None:
    """Test specific formats with Z suffix that might fail."""
    # These are the specific formats that might be problematic
    test_cases = [
        # Formats that isoparse might not handle but are common
        ("2022-10-15T04:53:30.315Z", datetime(2022, 10, 15, 4, 53, 30, 315000)),
        ("2022-10-15T04:53:30Z", datetime(2022, 10, 15, 4, 53, 30)),
        # Test that manual format list also works
        ("2022-10-15 04:53:30.315000", datetime(2022, 10, 15, 4, 53, 30, 315000)),
    ]

    for input_str, expected in test_cases:
        result = any_to_datetime(input_str)
        assert result is not None, f"Failed to parse {input_str}"
        # Compare without timezone
        if result.tzinfo:
            result = result.replace(tzinfo=None)
        assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"


def test_any_to_datetime_format_fallback() -> None:
    """Test that format fallback works when isoparse fails."""
    # A format that isoparse might not handle but is in DATE_FORMATS
    test_string = "2022.10.15 04:53:30.315"

    result = any_to_datetime(test_string)
    assert result is not None
    assert result == datetime(2022, 10, 15, 4, 53, 30, 315000)
