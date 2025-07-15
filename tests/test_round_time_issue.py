"""Tests for round_time issues - Issue #10."""

from datetime import date, datetime

import pytest

from time_helper import round_time


def test_round_time_always_returns_datetime() -> None:
    """Test that round_time always returns datetime objects, never date objects.

    This tests the fix for Issue #10.
    """
    # Test with various input types
    test_inputs = [
        "2022-02-10",  # String that could be parsed as date
        date(2022, 2, 10),  # Actual date object
        datetime(2022, 2, 10, 14, 30),  # Datetime object
        "2022-02-10 14:30:00",  # String with time
    ]

    for input_val in test_inputs:
        for freq in ["S", "M", "H", "D", "W", "m", "Y"]:
            dt_out = round_time(input_val, freq)  # type: ignore[arg-type]
            assert isinstance(dt_out, datetime), (
                f"Expected datetime but got {type(dt_out)} for input {input_val} with freq {freq}"
            )
            # Ensure it's not just a date - check that it has time components
            assert hasattr(dt_out, "hour"), f"Result missing time components for input {input_val} with freq {freq}"
            assert hasattr(dt_out, "minute"), f"Result missing time components for input {input_val} with freq {freq}"
            assert hasattr(dt_out, "second"), f"Result missing time components for input {input_val} with freq {freq}"


def test_round_time_week_edge_cases() -> None:
    """Test edge cases for week rounding that might return date instead of datetime."""
    # Test case from issue: any_to_datetime might return something that causes issues
    test_cases = [
        # (input, expected_monday, expected_sunday)
        ("2022-02-10", "2022-02-07T00:00:00", "2022-02-13T23:59:59.999999"),  # Thursday
        ("2022-02-07", "2022-02-07T00:00:00", "2022-02-13T23:59:59.999999"),  # Monday
        ("2022-02-13", "2022-02-07T00:00:00", "2022-02-13T23:59:59.999999"),  # Sunday
        (date(2022, 2, 10), "2022-02-07T00:00:00", "2022-02-13T23:59:59.999999"),  # date object
    ]

    for input_val, expected_min, expected_max in test_cases:
        # Test min (start of week)
        dt_out = round_time(input_val, "W", max_out=False)  # type: ignore[arg-type]
        assert isinstance(dt_out, datetime)
        assert dt_out.isoformat() == expected_min

        # Test max (end of week)
        dt_out = round_time(input_val, "W", max_out=True)  # type: ignore[arg-type]
        assert isinstance(dt_out, datetime)
        assert dt_out.isoformat() == expected_max


def test_round_time_preserves_timezone() -> None:
    """Test that round_time preserves timezone information."""
    from time_helper import localize_datetime

    # Create timezone-aware datetime
    dt = datetime(2022, 2, 10, 14, 30, 45)
    dt_utc = localize_datetime(dt, "UTC")
    dt_berlin = localize_datetime(dt, "Europe/Berlin")

    # Round with week
    dt_out_utc = round_time(dt_utc, "W")  # type: ignore[arg-type]
    dt_out_berlin = round_time(dt_berlin, "W")  # type: ignore[arg-type]

    assert isinstance(dt_out_utc, datetime)
    assert isinstance(dt_out_berlin, datetime)
    assert dt_out_utc.tzinfo is not None
    assert dt_out_berlin.tzinfo is not None
    assert dt_out_utc.tzinfo.tzname(dt_out_utc) == "UTC"
    # Europe/Berlin can be CET or CEST depending on date
    assert str(dt_out_berlin.tzinfo) == "Europe/Berlin"


def test_round_time_none_handling() -> None:
    """Test that round_time handles None input gracefully."""
    result = round_time(None, "D")  # type: ignore[arg-type]
    assert result is None

    result = round_time(None, "W")  # type: ignore[arg-type]
    assert result is None


def test_round_time_invalid_input() -> None:
    """Test that round_time handles invalid inputs appropriately."""
    with pytest.raises(ValueError, match="Could not parse Timestamp"):
        round_time("invalid date", "W")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Could not parse Timestamp"):
        round_time(object(), "W")  # type: ignore[arg-type]
