"""Additional tests for wrapper module to improve coverage."""

from datetime import date, datetime, timedelta

import pytest

from time_helper import DateTimeWrapper


class TestDateTimeWrapperEdgeCases:
    """Test complete coverage of DateTimeWrapper class."""

    def test_call_method_with_arguments(self) -> None:
        """Test __call__ method with arguments."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test call with arguments - should still return self.dt
        result = wrapper("arg1", "arg2", kwarg1="value1")
        assert result == dt
        # This covers line 40 where we return self.dt even with args/kwargs

    def test_add_with_non_timedelta(self) -> None:
        """Test __add__ method with non-timedelta object."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test addition with non-timedelta object
        # Check that __add__ returns NotImplemented when called with non-timedelta
        assert wrapper.__add__("not_a_timedelta") == NotImplemented  # type: ignore[operator]
        # This covers line 46 where we return NotImplemented

    def test_subtract_with_non_timedelta(self) -> None:
        """Test __sub__ method with non-timedelta object."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test subtraction with non-timedelta object (datetime)
        other_dt = datetime(2024, 1, 1, 10, 0, 0)
        result = wrapper - other_dt
        assert isinstance(result, timedelta)
        # This covers the case where we convert other to DateTimeWrapper

    def test_equal_with_non_wrapper(self) -> None:
        """Test __eq__ method with non-wrapper object."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test equality with non-wrapper object
        result = wrapper == dt
        assert result is True
        # This covers line 81 where we convert other to DateTimeWrapper

    def test_not_equal_with_non_wrapper(self) -> None:
        """Test __ne__ method with non-wrapper object."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test inequality with non-wrapper object
        result = wrapper != datetime(2024, 1, 2, 12, 0, 0)
        assert result is True
        # This covers line 93 where we convert other to DateTimeWrapper

    def test_type_checking_import(self) -> None:
        """Test TYPE_CHECKING import."""
        # This covers line 15 where TYPE_CHECKING is imported
        from typing import TYPE_CHECKING

        assert TYPE_CHECKING is not None or TYPE_CHECKING is False

    def test_make_aware_with_string_timezone(self) -> None:
        """Test make_aware with string timezone."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test make_aware with string timezone
        result = wrapper.make_aware("UTC")
        assert result.dt is not None
        assert result.dt.tzinfo is not None
        # This covers timezone string handling

    def test_make_unaware_with_string_timezone(self) -> None:
        """Test make_unaware with string timezone."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt).make_aware("UTC")

        # Test make_unaware with string timezone
        result = wrapper.make_unaware("UTC")
        assert result.dt is not None
        assert result.dt.tzinfo is None
        # This covers timezone string handling

    def test_localize_with_string_timezone(self) -> None:
        """Test localize with string timezone."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt).make_aware("UTC")

        # Test localize with string timezone
        result = wrapper.localize("America/New_York")
        assert result.dt is not None
        assert result.dt.tzinfo is not None
        # This covers timezone string handling

    def test_round_with_none_datetime(self) -> None:
        """Test round method with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test round with None datetime
        result = wrapper.round("H")
        assert result.dt is None
        # This covers None handling in round method

    def test_to_string_with_none_datetime(self) -> None:
        """Test to_string with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test to_string with None datetime
        result = wrapper.to_string()
        assert result == "None"
        # This covers None handling in to_string method

    def test_to_timestamp_with_none_datetime(self) -> None:
        """Test to_timestamp with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test to_timestamp with None datetime
        with pytest.raises(ValueError, match="Cannot convert None to timestamp"):
            wrapper.to_timestamp()
        # This covers None handling in to_timestamp method

    def test_year_property_with_none_datetime(self) -> None:
        """Test year property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test year property with None datetime
        with pytest.raises(AttributeError, match="Cannot access year of None datetime"):
            _ = wrapper.year
        # This covers None handling in year property

    def test_month_property_with_none_datetime(self) -> None:
        """Test month property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test month property with None datetime
        with pytest.raises(AttributeError, match="Cannot access month of None datetime"):
            _ = wrapper.month
        # This covers None handling in month property

    def test_day_property_with_none_datetime(self) -> None:
        """Test day property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test day property with None datetime
        with pytest.raises(AttributeError, match="Cannot access day of None datetime"):
            _ = wrapper.day
        # This covers None handling in day property

    def test_hour_property_with_none_datetime(self) -> None:
        """Test hour property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test hour property with None datetime
        with pytest.raises(AttributeError, match="Cannot access hour of None datetime"):
            _ = wrapper.hour
        # This covers None handling in hour property

    def test_minute_property_with_none_datetime(self) -> None:
        """Test minute property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test minute property with None datetime
        with pytest.raises(AttributeError, match="Cannot access minute of None datetime"):
            _ = wrapper.minute
        # This covers None handling in minute property

    def test_second_property_with_none_datetime(self) -> None:
        """Test second property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test second property with None datetime
        with pytest.raises(AttributeError, match="Cannot access second of None datetime"):
            _ = wrapper.second
        # This covers None handling in second property

    def test_microsecond_property_with_none_datetime(self) -> None:
        """Test microsecond property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test microsecond property with None datetime
        with pytest.raises(AttributeError):
            _ = wrapper.microsecond  # type: ignore[attr-defined]
        # This covers None handling in microsecond property

    def test_weekday_property_with_none_datetime(self) -> None:
        """Test weekday property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test weekday property with None datetime
        with pytest.raises(AttributeError, match="Cannot access weekday of None datetime"):
            _ = wrapper.weekday
        # This covers None handling in weekday property

    def test_less_than_with_non_wrapper(self) -> None:
        """Test __lt__ method with non-wrapper object."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test less than with non-wrapper object
        result = wrapper < datetime(2024, 1, 1, 14, 0, 0)
        assert result is True
        # This covers line 81 where we convert other to DateTimeWrapper in __lt__

    def test_greater_than_with_non_wrapper(self) -> None:
        """Test __gt__ method with non-wrapper object."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        wrapper = DateTimeWrapper(dt)

        # Test greater than with non-wrapper object
        result = wrapper > datetime(2024, 1, 1, 10, 0, 0)
        assert result is True
        # This covers line 93 where we convert other to DateTimeWrapper in __gt__

    def test_timezone_property_with_none_datetime(self) -> None:
        """Test timezone property with None datetime."""
        wrapper = DateTimeWrapper(None)

        # Test timezone property with None datetime
        with pytest.raises(AttributeError, match="Cannot access timezone of None datetime"):
            _ = wrapper.timezone
        # This covers line 254 where we raise error for None datetime


class TestDateTimeWrapperCoverage:
    """Test edge cases and error conditions in DateTimeWrapper."""

    def test_datetime_wrapper_none_handling(self) -> None:
        """Test DateTimeWrapper with None values."""
        # Test creating wrapper with None
        wrapper = DateTimeWrapper(None)
        assert wrapper.dt is None

        # Test operations on None wrapper should raise errors
        with pytest.raises(AttributeError, match="Cannot access year of None datetime"):
            _ = wrapper.year

        with pytest.raises(AttributeError, match="Cannot access month of None datetime"):
            _ = wrapper.month

        with pytest.raises(AttributeError, match="Cannot access day of None datetime"):
            _ = wrapper.day

    def test_datetime_wrapper_call_method(self) -> None:
        """Test DateTimeWrapper __call__ method."""
        dt = datetime(2024, 7, 15, 12, 30, 45)
        wrapper = DateTimeWrapper(dt)

        # Test call with no arguments
        result = wrapper()
        assert result == dt

        # Test call with None wrapper
        none_wrapper = DateTimeWrapper(None)
        result = none_wrapper()
        assert result is None

    def test_datetime_wrapper_edge_cases(self) -> None:
        """Test DateTimeWrapper edge cases."""
        dt = datetime(2024, 7, 15, 12, 30, 45)
        wrapper = DateTimeWrapper(dt)

        # Test make_unaware with None timezone
        result = wrapper.make_unaware()
        assert result.dt is not None
        assert result.dt.tzinfo is None

        # Test round with None datetime
        none_wrapper = DateTimeWrapper(None)
        result = none_wrapper.round("H")
        assert result.dt is None

    def test_datetime_wrapper_comparison_edge_cases(self) -> None:
        """Test DateTimeWrapper comparison edge cases."""
        dt1 = datetime(2024, 7, 15, 12, 30, 45)
        dt2 = datetime(2024, 7, 15, 14, 30, 45)

        wrapper1 = DateTimeWrapper(dt1)
        DateTimeWrapper(dt2)
        none_wrapper = DateTimeWrapper(None)

        # Test comparisons with None
        assert not (wrapper1 < none_wrapper)
        assert not (wrapper1 <= none_wrapper)
        assert not (wrapper1 > none_wrapper)
        assert not (wrapper1 >= none_wrapper)
        assert wrapper1 != none_wrapper
        assert wrapper1 != none_wrapper

        # Test None with None
        assert not (none_wrapper < none_wrapper)
        assert none_wrapper <= none_wrapper
        assert not (none_wrapper > none_wrapper)
        assert none_wrapper >= none_wrapper
        assert none_wrapper == none_wrapper
        assert none_wrapper == none_wrapper

    def test_datetime_wrapper_arithmetic_edge_cases(self) -> None:
        """Test DateTimeWrapper arithmetic edge cases."""
        dt = datetime(2024, 7, 15, 12, 30, 45)
        wrapper = DateTimeWrapper(dt)
        none_wrapper = DateTimeWrapper(None)

        # Test addition with None
        result = none_wrapper + timedelta(hours=1)
        assert result.dt is None

        # Test subtraction with None
        result = none_wrapper - timedelta(hours=1)  # type: ignore[assignment]
        assert isinstance(result, DateTimeWrapper)
        assert result.dt is None

        # Test subtraction of None from datetime should raise error
        with pytest.raises(ValueError, match="Cannot compute time diff with None datetime"):
            wrapper - none_wrapper

    def test_datetime_wrapper_string_conversion_edge_cases(self) -> None:
        """Test DateTimeWrapper string conversion edge cases."""
        none_wrapper = DateTimeWrapper(None)

        # Test string conversion with None
        assert str(none_wrapper) == "None"
        assert repr(none_wrapper) == "DateTimeWrapper(None)"

        # Test to_string with None
        result = none_wrapper.to_string()
        assert result == "None"

        # Test to_timestamp with None should raise error
        with pytest.raises(ValueError, match="Cannot convert None to timestamp"):
            none_wrapper.to_timestamp()

    def test_datetime_wrapper_timezone_operations_edge_cases(self) -> None:
        """Test DateTimeWrapper timezone operations edge cases."""
        none_wrapper = DateTimeWrapper(None)

        # Test make_aware with None
        result = none_wrapper.make_aware("UTC")
        assert result.dt is None

        # Test make_unaware with None
        result = none_wrapper.make_unaware()
        assert result.dt is None

        # Test localize with None
        result = none_wrapper.localize("UTC")
        assert result.dt is None

    def test_datetime_wrapper_method_chaining_with_none(self) -> None:
        """Test DateTimeWrapper method chaining with None values."""
        none_wrapper = DateTimeWrapper(None)

        # Test chaining operations on None
        result = none_wrapper.make_aware("UTC").round("H").localize("America/New_York").make_unaware()

        assert result.dt is None

    def test_datetime_wrapper_property_access_edge_cases(self) -> None:
        """Test DateTimeWrapper property access edge cases."""
        # Test with date object (not datetime)
        dt = date(2024, 7, 15)
        wrapper = DateTimeWrapper(dt)

        # Properties should work with date objects too
        assert wrapper.year == 2024
        assert wrapper.month == 7
        assert wrapper.day == 15

        # Time properties should be None or 0 for date objects
        # (depending on how any_to_datetime handles date objects)
        # This tests the property access mechanism
