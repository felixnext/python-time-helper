"""Simple tests to improve coverage without complex mocking."""

from datetime import datetime

from time_helper.ops import time_diff


def test_time_diff_edge_cases() -> None:
    """Test time_diff with various edge cases."""
    dt1 = datetime(2024, 1, 1, 12, 0, 0)
    dt2 = datetime(2024, 1, 1, 10, 0, 0)

    # Test with explicit None timezone
    result = time_diff(dt1, dt2, tz=None)
    assert result.total_seconds() == 2 * 3600

    # Test with empty string timezone
    result = time_diff(dt1, dt2, tz="")
    assert result.total_seconds() == 2 * 3600


def test_any_to_datetime_edge_cases() -> None:
    """Test any_to_datetime with edge cases."""
    from time_helper.convert import any_to_datetime

    # Test with empty string
    result = any_to_datetime("")
    assert result is None

    # Test with None
    result = any_to_datetime(None)
    assert result is None


def test_round_time_edge_cases() -> None:
    """Test round_time with edge cases."""
    from time_helper.ops import round_time

    # Test with None input
    result = round_time(None, "H")  # type: ignore[arg-type]
    assert result is None
