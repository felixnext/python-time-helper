"""Tests for DateTimeWrapper class - Issue #3."""

from datetime import date, datetime, timedelta

import pytest

from time_helper import DateTimeWrapper, make_aware


class TestDateTimeWrapperCreation:
    """Test DateTimeWrapper initialization with various inputs."""

    def test_create_from_string(self) -> None:
        """Test creating wrapper from string."""
        dtw = DateTimeWrapper("2024-03-15 10:30:00")
        assert dtw.dt is not None
        assert dtw.dt.year == 2024
        assert dtw.dt.month == 3
        assert dtw.dt.day == 15
        assert dtw.dt.hour == 10
        assert dtw.dt.minute == 30

    def test_create_from_datetime(self) -> None:
        """Test creating wrapper from datetime object."""
        dt = datetime(2024, 3, 15, 10, 30)
        dtw = DateTimeWrapper(dt)
        assert dtw.dt == dt

    def test_create_from_date(self) -> None:
        """Test creating wrapper from date object."""
        d = date(2024, 3, 15)
        dtw = DateTimeWrapper(d)
        assert dtw.dt is not None
        assert dtw.dt.date() == d
        assert dtw.dt.time().hour == 0
        assert dtw.dt.time().minute == 0

    def test_create_from_timestamp(self) -> None:
        """Test creating wrapper from unix timestamp."""
        ts = 1710501045  # 2024-03-15 10:30:45 UTC
        dtw = DateTimeWrapper(ts)
        assert dtw.dt is not None
        assert dtw.dt.year == 2024

    def test_create_from_none(self) -> None:
        """Test creating wrapper from None."""
        dtw = DateTimeWrapper(None)
        assert dtw.dt is None

    def test_create_from_wrapper(self) -> None:
        """Test creating wrapper from another wrapper."""
        dtw1 = DateTimeWrapper("2024-03-15 10:30:00")
        dtw2 = DateTimeWrapper(dtw1)
        assert dtw2.dt == dtw1.dt


class TestDateTimeWrapperCall:
    """Test DateTimeWrapper callable interface."""

    def test_call_without_args(self) -> None:
        """Test calling wrapper without arguments returns datetime."""
        dt = datetime(2024, 3, 15, 10, 30)
        dtw = DateTimeWrapper(dt)
        result = dtw()
        assert result == dt

    def test_call_none_wrapper(self) -> None:
        """Test calling wrapper with None datetime."""
        dtw = DateTimeWrapper(None)
        result = dtw()
        assert result is None


class TestDateTimeWrapperOperators:
    """Test DateTimeWrapper operator overloading."""

    def test_subtract_wrappers(self) -> None:
        """Test subtracting two wrappers."""
        dtw1 = DateTimeWrapper("2024-03-15 15:30:00")
        dtw2 = DateTimeWrapper("2024-03-15 10:30:00")
        diff = dtw1 - dtw2
        assert isinstance(diff, timedelta)
        assert diff == timedelta(hours=5)

    def test_subtract_wrapper_from_datetime(self) -> None:
        """Test subtracting datetime from wrapper."""
        dtw = DateTimeWrapper("2024-03-15 15:30:00")
        dt = datetime(2024, 3, 15, 10, 30)
        diff = dtw - dt
        assert isinstance(diff, timedelta)
        assert diff == timedelta(hours=5)

    def test_subtract_string_from_wrapper(self) -> None:
        """Test subtracting string date from wrapper."""
        dtw = DateTimeWrapper("2024-03-15 15:30:00")
        diff = dtw - "2024-03-15 10:30:00"
        assert isinstance(diff, timedelta)
        assert diff == timedelta(hours=5)

    def test_subtract_with_timezone_awareness(self) -> None:
        """Test subtraction handles timezone-aware datetimes."""
        dt1 = make_aware("2024-03-15 15:30:00", "UTC")
        dt2 = make_aware("2024-03-15 10:30:00", "America/New_York")
        dtw1 = DateTimeWrapper(dt1)
        dtw2 = DateTimeWrapper(dt2)

        # NYC is UTC-4 in March, so 10:30 NYC = 14:30 UTC
        # 15:30 UTC - 14:30 UTC = 1 hour
        diff = dtw1 - dtw2
        assert isinstance(diff, timedelta)
        assert diff == timedelta(hours=1)

    def test_subtract_none_raises_error(self) -> None:
        """Test subtracting None raises ValueError."""
        dtw = DateTimeWrapper("2024-03-15")
        none_dtw = DateTimeWrapper(None)

        with pytest.raises(ValueError, match="Cannot compute time diff with None datetime"):
            dtw - none_dtw

        with pytest.raises(ValueError, match="Cannot compute time diff with None datetime"):
            none_dtw - dtw

    def test_add_timedelta(self) -> None:
        """Test adding timedelta to wrapper."""
        dtw = DateTimeWrapper("2024-03-15 10:30:00")
        result = dtw + timedelta(hours=5)
        assert isinstance(result, DateTimeWrapper)
        assert result.dt is not None
        assert result.dt.hour == 15

    def test_subtract_timedelta(self) -> None:
        """Test subtracting timedelta from wrapper."""
        dtw = DateTimeWrapper("2024-03-15 10:30:00")
        result = dtw - timedelta(hours=2)
        assert isinstance(result, DateTimeWrapper)
        assert result.dt is not None
        assert result.dt.hour == 8

    def test_comparison_operators(self) -> None:
        """Test comparison operators between wrappers."""
        dtw1 = DateTimeWrapper("2024-03-15 10:30:00")
        dtw2 = DateTimeWrapper("2024-03-15 15:30:00")
        dtw3 = DateTimeWrapper("2024-03-15 10:30:00")

        assert dtw1 < dtw2
        assert dtw2 > dtw1
        assert dtw1 <= dtw2
        assert dtw2 >= dtw1
        assert dtw1 == dtw3
        assert dtw1 != dtw2


class TestDateTimeWrapperMethods:
    """Test DateTimeWrapper methods for datetime operations."""

    def test_make_aware(self) -> None:
        """Test making wrapper timezone-aware."""
        dtw = DateTimeWrapper("2024-03-15 10:30:00")
        aware_dtw = dtw.make_aware("UTC")
        assert isinstance(aware_dtw, DateTimeWrapper)
        assert aware_dtw.dt is not None
        assert aware_dtw.dt.tzinfo is not None
        assert str(aware_dtw.dt.tzinfo) == "UTC"

    def test_make_unaware(self) -> None:
        """Test making wrapper timezone-unaware."""
        dt = make_aware("2024-03-15 10:30:00", "UTC")
        dtw = DateTimeWrapper(dt)
        unaware_dtw = dtw.make_unaware()
        assert isinstance(unaware_dtw, DateTimeWrapper)
        assert unaware_dtw.dt is not None
        assert unaware_dtw.dt.tzinfo is None

    def test_localize(self) -> None:
        """Test localizing wrapper to different timezone."""
        dt = make_aware("2024-03-15 10:30:00", "UTC")
        dtw = DateTimeWrapper(dt)
        tokyo_dtw = dtw.localize("Asia/Tokyo")
        assert isinstance(tokyo_dtw, DateTimeWrapper)
        assert tokyo_dtw.dt is not None
        assert str(tokyo_dtw.dt.tzinfo) == "Asia/Tokyo"
        assert tokyo_dtw.dt.hour == 19  # UTC+9

    def test_round_time(self) -> None:
        """Test rounding time in wrapper."""
        dtw = DateTimeWrapper("2024-03-15 10:35:45")

        # Round to hour
        hour_dtw = dtw.round("H")
        assert isinstance(hour_dtw, DateTimeWrapper)
        assert hour_dtw.dt is not None
        assert hour_dtw.dt.hour == 10
        assert hour_dtw.dt.minute == 0
        assert hour_dtw.dt.second == 0

        # Round to day
        day_dtw = dtw.round("D")
        assert day_dtw.dt is not None
        assert day_dtw.dt.hour == 0
        assert day_dtw.dt.minute == 0

        # Round with max_out
        day_end_dtw = dtw.round("D", max_out=True)
        assert day_end_dtw.dt is not None
        assert day_end_dtw.dt.hour == 23
        assert day_end_dtw.dt.minute == 59
        assert day_end_dtw.dt.second == 59

    def test_to_string(self) -> None:
        """Test converting wrapper to string."""
        dtw = DateTimeWrapper("2024-03-15 10:30:00")

        # Default ISO format
        assert dtw.to_string() == "2024-03-15T10:30:00"

        # Custom format
        assert dtw.to_string("%Y-%m-%d") == "2024-03-15"
        assert dtw.to_string("%H:%M") == "10:30"

    def test_to_timestamp(self) -> None:
        """Test converting wrapper to unix timestamp."""
        dt = make_aware("2024-03-15 10:30:00", "UTC")
        dtw = DateTimeWrapper(dt)
        ts = dtw.to_timestamp()
        assert isinstance(ts, (int, float))
        assert ts > 0

    def test_date_time_properties(self) -> None:
        """Test accessing date and time properties."""
        dtw = DateTimeWrapper("2024-03-15 10:30:45")

        # Date properties
        assert dtw.year == 2024
        assert dtw.month == 3
        assert dtw.day == 15

        # Time properties
        assert dtw.hour == 10
        assert dtw.minute == 30
        assert dtw.second == 45

        # Day of week (0 = Monday)
        assert dtw.weekday == 4  # Friday

        # Timezone property
        assert dtw.timezone is None  # Unaware

        aware_dtw = dtw.make_aware("UTC")
        assert aware_dtw.timezone is not None


class TestDateTimeWrapperChaining:
    """Test method chaining with DateTimeWrapper."""

    def test_chaining_operations(self) -> None:
        """Test chaining multiple operations."""
        dtw = DateTimeWrapper("2024-03-15 10:35:45")

        # Chain: make aware -> round to hour -> convert timezone
        result = dtw.make_aware("UTC").round("H").localize("Asia/Tokyo")

        assert isinstance(result, DateTimeWrapper)
        assert result.dt is not None
        assert result.dt.minute == 0  # Rounded
        assert str(result.dt.tzinfo) == "Asia/Tokyo"  # Converted
        assert result.dt.hour == 19  # UTC 10:00 -> Tokyo 19:00

    def test_chaining_with_none(self) -> None:
        """Test chaining handles None gracefully."""
        dtw = DateTimeWrapper(None)
        result = dtw.make_aware("UTC").round("H")
        assert isinstance(result, DateTimeWrapper)
        assert result.dt is None


class TestDateTimeWrapperStringRepresentation:
    """Test string representations of DateTimeWrapper."""

    def test_str_representation(self) -> None:
        """Test __str__ method."""
        dtw = DateTimeWrapper("2024-03-15 10:30:00")
        assert str(dtw) == "2024-03-15T10:30:00"

        dtw_none = DateTimeWrapper(None)
        assert str(dtw_none) == "None"

    def test_repr_representation(self) -> None:
        """Test __repr__ method."""
        dtw = DateTimeWrapper("2024-03-15 10:30:00")
        assert repr(dtw) == "DateTimeWrapper(2024-03-15T10:30:00)"

        dtw_none = DateTimeWrapper(None)
        assert repr(dtw_none) == "DateTimeWrapper(None)"


class TestDateTimeWrapperEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_input(self) -> None:
        """Test wrapper with invalid input."""
        with pytest.raises(ValueError):
            DateTimeWrapper("invalid date string")

    def test_operations_on_none(self) -> None:
        """Test operations on wrapper with None datetime."""
        dtw = DateTimeWrapper(None)

        # These should return wrapper with None
        assert dtw.make_aware("UTC").dt is None
        assert dtw.round("H").dt is None
        assert dtw.make_unaware().dt is None

        # These should raise or return None
        assert dtw.to_string() == "None"

        with pytest.raises(AttributeError):
            _ = dtw.year

    def test_timezone_preservation(self) -> None:
        """Test that timezone info is preserved through operations."""
        dt = make_aware("2024-03-15 10:30:00", "Europe/Berlin")
        dtw = DateTimeWrapper(dt)

        # Adding timedelta should preserve timezone
        result = dtw + timedelta(hours=5)
        assert result.dt is not None
        assert result.dt.tzinfo is not None
        assert str(result.dt.tzinfo) == "Europe/Berlin"

        # Rounding should preserve timezone
        rounded = dtw.round("H")
        assert rounded.dt is not None
        assert rounded.dt.tzinfo is not None
        assert str(rounded.dt.tzinfo) == "Europe/Berlin"
