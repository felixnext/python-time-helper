"""Complete test coverage for natural.py module."""

import re
from datetime import datetime

import pytest

from time_helper.natural import add_natural_language_support, parse_natural


class TestNaturalLanguageEdgeCases:
    """Test complete coverage of natural language parsing."""

    def test_weekday_when_days_ahead_is_zero(self) -> None:
        """Test weekday parsing when target day would have days_ahead < 0."""
        # Sunday, July 14, 2024
        ref_date = datetime(2024, 7, 14, 12, 0, 0)
        assert ref_date.weekday() == 6  # Confirm it's Sunday

        # Asking for "monday" on Sunday - days_ahead would be 1-6 = -5
        # So it should add 7 to get 2 days ahead
        result = parse_natural("monday", reference=ref_date)
        assert result.day == 15  # Next day (Monday)
        assert result.weekday() == 0

    def test_next_month_december_edge_case(self) -> None:
        """Test 'next month' when in December - should wrap to next year."""
        # December 15, 2024
        ref_date = datetime(2024, 12, 15, 12, 0, 0)

        # This tests line 263 - when month is 12
        result = parse_natural("next month", reference=ref_date)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15

    def test_next_month_december(self) -> None:
        """Test 'next month' in December."""
        # Test when current month is December
        ref_date = datetime(2024, 12, 15, 12, 0, 0)
        result = parse_natural("next month", reference=ref_date)

        # Should go to January next year
        assert result.year == 2025
        assert result.month == 1
        # This covers line 87 where we handle December -> January

    def test_last_month_january(self) -> None:
        """Test 'last month' in January."""
        # Test when current month is January
        ref_date = datetime(2024, 1, 15, 12, 0, 0)
        result = parse_natural("last month", reference=ref_date)

        # Should go to December previous year
        assert result.year == 2023
        assert result.month == 12
        # This covers line 92 where we handle January -> December

    def test_time_with_am_pm(self) -> None:
        """Test time parsing with AM/PM."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test various AM/PM patterns
        result = parse_natural("9 am", reference=ref_date)
        assert result.hour == 9

        result = parse_natural("2 pm", reference=ref_date)
        assert result.hour == 14

        result = parse_natural("11:30 am", reference=ref_date)
        assert result.hour == 11
        assert result.minute == 30

        result = parse_natural("5:45 pm", reference=ref_date)
        assert result.hour == 17
        assert result.minute == 45

    def test_specific_time_formats(self) -> None:
        """Test specific time formats."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test 24-hour format patterns that are actually implemented
        result = parse_natural("2:30 pm", reference=ref_date)
        assert result.hour == 14
        assert result.minute == 30

        # Test noon and midnight
        result = parse_natural("noon", reference=ref_date)
        assert result.hour == 12
        assert result.minute == 0

        result = parse_natural("midnight", reference=ref_date)
        assert result.hour == 0
        assert result.minute == 0

    def test_relative_time_expressions(self) -> None:
        """Test relative time expressions."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test "in X time" patterns
        result = parse_natural("in 3 hours", reference=ref_date)
        assert result.hour == 15

        result = parse_natural("in 45 minutes", reference=ref_date)
        assert result.minute == 45

        result = parse_natural("in 2 days", reference=ref_date)
        assert result.day == 17

        result = parse_natural("in 1 week", reference=ref_date)
        assert result.day == 22

    def test_ago_time_expressions(self) -> None:
        """Test 'ago' time expressions."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test "X ago" patterns
        result = parse_natural("2 hours ago", reference=ref_date)
        assert result.hour == 10

        result = parse_natural("30 minutes ago", reference=ref_date)
        assert result.minute == 30

        result = parse_natural("3 days ago", reference=ref_date)
        assert result.day == 12

        result = parse_natural("1 week ago", reference=ref_date)
        assert result.day == 8

    def test_specific_weekday_patterns(self) -> None:
        """Test specific weekday patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Test weekday names
        result = parse_natural("tuesday", reference=ref_date)
        assert result.weekday() == 1  # Tuesday

        result = parse_natural("friday", reference=ref_date)
        assert result.weekday() == 4  # Friday

        result = parse_natural("sunday", reference=ref_date)
        assert result.weekday() == 6  # Sunday

    def test_next_weekday_patterns(self) -> None:
        """Test next weekday patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Test next weekday
        result = parse_natural("next tuesday", reference=ref_date)
        assert result.weekday() == 1  # Tuesday
        assert result.day == 16  # Next Tuesday (tomorrow)

        result = parse_natural("next friday", reference=ref_date)
        assert result.weekday() == 4  # Friday
        assert result.day == 19  # This Friday

    def test_last_weekday_patterns(self) -> None:
        """Test last weekday patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Test last weekday
        result = parse_natural("last friday", reference=ref_date)
        assert result.weekday() == 4  # Friday
        assert result.day == 12  # Last Friday

        result = parse_natural("last sunday", reference=ref_date)
        assert result.weekday() == 6  # Sunday
        assert result.day == 14  # Last Sunday

    def test_weekend_patterns(self) -> None:
        """Test weekend patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Test weekend references
        result = parse_natural("this weekend", reference=ref_date)
        assert result.weekday() == 5  # Saturday

        result = parse_natural("next weekend", reference=ref_date)
        assert result.weekday() == 5  # Saturday
        assert result.day == 27  # Next Saturday

    def test_business_day_patterns(self) -> None:
        """Test business day patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Test business day references
        result = parse_natural("next business day", reference=ref_date)
        assert result.weekday() == 1  # Tuesday

        # Test from Friday
        friday_ref = datetime(2024, 7, 19, 12, 0, 0)  # Friday
        result = parse_natural("next business day", reference=friday_ref)
        assert result.weekday() == 0  # Monday

    def test_ordinal_patterns(self) -> None:
        """Test ordinal patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test ordinal references
        result = parse_natural("first of the month", reference=ref_date)
        assert result.day == 1

        result = parse_natural("last day of the month", reference=ref_date)
        assert result.day == 31

        result = parse_natural("15th of next month", reference=ref_date)
        assert result.day == 15
        assert result.month == 8

    def test_time_range_patterns(self) -> None:
        """Test time range patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test time ranges
        result = parse_natural("morning", reference=ref_date)
        assert 6 <= result.hour <= 11

        result = parse_natural("afternoon", reference=ref_date)
        assert 12 <= result.hour <= 17

        result = parse_natural("evening", reference=ref_date)
        assert 18 <= result.hour <= 21

        result = parse_natural("night", reference=ref_date)
        assert result.hour >= 22 or result.hour <= 5

    def test_date_boundary_patterns(self) -> None:
        """Test date boundary patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test boundary references
        result = parse_natural("beginning of month", reference=ref_date)
        assert result.day == 1

        result = parse_natural("end of month", reference=ref_date)
        assert result.day == 31

        result = parse_natural("beginning of year", reference=ref_date)
        assert result.month == 1
        assert result.day == 1

        result = parse_natural("end of year", reference=ref_date)
        assert result.month == 12
        assert result.day == 31

    def test_complex_with_at_patterns(self) -> None:
        """Test complex patterns with 'at'."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test complex expressions with 'at'
        result = parse_natural("tomorrow at 9am", reference=ref_date)
        assert result.day == 16
        assert result.hour == 9

        result = parse_natural("friday at 2:30pm", reference=ref_date)
        assert result.weekday() == 4
        assert result.hour == 14
        assert result.minute == 30

        result = parse_natural("next week at noon", reference=ref_date)
        assert result.hour == 12
        assert result.minute == 0

    def test_timezone_aware_parsing(self) -> None:
        """Test timezone-aware parsing."""
        from time_helper import make_aware

        ref_date = make_aware("2024-07-15 12:00:00", "America/New_York")

        # Test with timezone-aware reference
        result = parse_natural("tomorrow", reference=ref_date)
        assert result.tzinfo == ref_date.tzinfo
        assert result.day == 16

    def test_error_cases(self) -> None:
        """Test error cases."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test invalid expressions
        with pytest.raises(ValueError, match="Empty expression"):
            parse_natural("", reference=ref_date)

        with pytest.raises(ValueError, match="Empty expression"):
            parse_natural("   ", reference=ref_date)

        with pytest.raises(ValueError, match="Cannot parse natural language expression"):
            parse_natural("invalid expression", reference=ref_date)

        with pytest.raises(ValueError, match="Cannot parse natural language expression"):
            parse_natural("gibberish", reference=ref_date)

    def test_edge_case_patterns(self) -> None:
        """Test edge case patterns."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test case sensitivity
        result = parse_natural("TODAY", reference=ref_date)
        assert result.date() == ref_date.date()

        result = parse_natural("Tomorrow", reference=ref_date)
        assert result.day == 16

        result = parse_natural("NEXT MONDAY", reference=ref_date)
        assert result.weekday() == 0

    def test_next_weekend_when_already_saturday(self) -> None:
        """Test 'next weekend' when reference date is already Saturday."""
        # Saturday, July 20, 2024
        ref_date = datetime(2024, 7, 20, 12, 0, 0)
        assert ref_date.weekday() == 5  # Confirm it's Saturday

        result = parse_natural("next weekend", reference=ref_date)
        # Should go to next Saturday (7 + 7 = 14 days later)
        assert result.day == 3  # August 3
        assert result.month == 8
        assert result.weekday() == 5

    def test_last_weekend_when_already_saturday(self) -> None:
        """Test 'last weekend' when reference date is already Saturday."""
        # Saturday, July 20, 2024
        ref_date = datetime(2024, 7, 20, 12, 0, 0)
        assert ref_date.weekday() == 5  # Confirm it's Saturday

        result = parse_natural("last weekend", reference=ref_date)
        # Should go to last Saturday (7 days earlier)
        assert result.day == 13
        assert result.weekday() == 5

    def test_weekday_when_days_ahead_is_zero_2(self) -> None:
        """Test weekday parsing when target day is today."""
        # Monday, July 15, 2024
        ref_date = datetime(2024, 7, 15, 12, 0, 0)
        assert ref_date.weekday() == 0  # Confirm it's Monday

        result = parse_natural("monday", reference=ref_date)
        # When the target day is today (days_ahead = 0), it returns today
        assert result.day == 15  # Same Monday
        assert result.weekday() == 0

    def test_time_with_12am(self) -> None:
        """Test time parsing with 12 am (midnight)."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        result = parse_natural("12 am", reference=ref_date)
        assert result.hour == 0  # 12 am should be 0 hours
        assert result.minute == 0

    def test_time_patterns_that_exist_in_code(self) -> None:
        """Test specific time patterns that are in the code."""
        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Test patterns with 'at'
        result = parse_natural("today at 3 pm", reference=ref_date)
        assert result.hour == 15
        assert result.day == 15

        # Test the 'the month' pattern
        result = parse_natural("15th of the month", reference=ref_date)
        assert result.day == 15
        assert result.month == 7

    def test_add_natural_language_support_functionality(self) -> None:
        """Test the add_natural_language_support function."""
        # Import DateTimeWrapper
        from time_helper.wrapper import DateTimeWrapper

        # Store original __init__ to restore later
        original_init = DateTimeWrapper.__init__

        try:
            # Apply natural language support
            add_natural_language_support()

            # Test that natural language parsing works in __init__
            wrapper = DateTimeWrapper("tomorrow", reference=datetime(2024, 7, 15, 12, 0, 0))  # type: ignore[call-arg]
            assert wrapper.dt.day == 16  # type: ignore[union-attr]

            # Test with invalid natural language (should fall back to regular parsing)
            wrapper = DateTimeWrapper("2024-07-15")
            assert wrapper.dt.day == 15  # type: ignore[union-attr]

            # Test add_natural method
            wrapper = DateTimeWrapper(datetime(2024, 7, 15, 12, 0, 0))
            result = wrapper.add_natural("2 days")  # type: ignore[attr-defined]
            assert result.dt.day == 17

            # Test add_natural with None datetime
            wrapper = DateTimeWrapper(None)
            with pytest.raises(ValueError, match="Cannot add to None datetime"):
                wrapper.add_natural("tomorrow")  # type: ignore[attr-defined]

            # Test add_natural with complex expression
            wrapper = DateTimeWrapper(datetime(2024, 7, 15, 12, 0, 0))
            result = wrapper.add_natural("next monday")  # type: ignore[attr-defined]
            # Monday July 15 -> next Monday July 22
            assert result.dt.weekday() == 0
            assert result.dt.day == 22

            # The parse_natural method doesn't exist, only add_natural
            # So we test the natural language parsing in __init__ instead
            wrapper2 = DateTimeWrapper("tomorrow at 3pm", reference=datetime(2024, 7, 15, 12, 0, 0))  # type: ignore[call-arg]
            assert wrapper2.dt.day == 16  # type: ignore[union-attr]
            assert wrapper2.dt.hour == 15  # type: ignore[union-attr]

        finally:
            # Restore original __init__
            DateTimeWrapper.__init__ = original_init  # type: ignore[method-assign]

    def test_add_natural_with_simple_duration(self) -> None:
        """Test add_natural with simple duration expressions."""
        from time_helper.wrapper import DateTimeWrapper

        # Store original to restore later
        original_init = DateTimeWrapper.__init__

        try:
            add_natural_language_support()

            # Test simple duration patterns that match the regex
            wrapper = DateTimeWrapper(datetime(2024, 7, 15, 12, 0, 0))

            # These should be treated as relative offsets
            result = wrapper.add_natural("1 day")  # type: ignore[attr-defined]
            assert result.dt.day == 16

            result = wrapper.add_natural("3 hours")  # type: ignore[attr-defined]
            assert result.dt.hour == 15

            result = wrapper.add_natural("2 weeks")  # type: ignore[attr-defined]
            assert result.dt.day == 29

        finally:
            DateTimeWrapper.__init__ = original_init  # type: ignore[method-assign]

    def test_complex_offset_calculation_in_add_natural(self) -> None:
        """Test complex offset calculation path in add_natural."""
        from time_helper.wrapper import DateTimeWrapper

        original_init = DateTimeWrapper.__init__

        try:
            add_natural_language_support()

            wrapper = DateTimeWrapper(datetime(2024, 7, 15, 12, 0, 0))

            # Use an expression that doesn't match the simple duration regex
            # This will go through the complex offset calculation path
            result = wrapper.add_natural("tomorrow")  # type: ignore[attr-defined]
            assert result.dt.day == 16

            # The complex path calculates: offset_dt - self.dt, then adds it back
            # This tests lines 309-317

        finally:
            DateTimeWrapper.__init__ = original_init  # type: ignore[method-assign]

    def test_patterns_not_matching_simple_duration_regex(self) -> None:
        """Test patterns that don't match the simple duration regex."""
        # Test the regex used in add_natural
        pattern = re.compile(r"^\d+ (hour|hours|minute|minutes|day|days|week|weeks)$")

        # These should NOT match
        assert not pattern.match("in 1 day")
        assert not pattern.match("1 day ago")
        assert not pattern.match("tomorrow")
        assert not pattern.match("next week")

        # These SHOULD match
        assert pattern.match("1 day")
        assert pattern.match("2 hours")
        assert pattern.match("3 weeks")
        assert pattern.match("10 minutes")
