"""Simple test to achieve 100% coverage for natural.py."""

from datetime import datetime, timedelta

import pytest

from time_helper import make_aware
from time_helper.natural import parse_natural


class TestNaturalLanguageParsing:
    """Test natural language datetime parsing."""

    def test_parse_relative_days(self) -> None:
        """Test parsing relative day expressions."""
        # Note: These are proposed functions that don't exist yet
        # We're writing the test first (TDD)
        from time_helper import parse_natural

        # Test relative to a fixed reference date
        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Basic relative days
        result = parse_natural("today", reference=ref_date)
        assert result.date() == ref_date.date()

        result = parse_natural("tomorrow", reference=ref_date)
        assert result.date() == (ref_date + timedelta(days=1)).date()

        result = parse_natural("yesterday", reference=ref_date)
        assert result.date() == (ref_date - timedelta(days=1)).date()

        # Days of the week
        result = parse_natural("monday", reference=ref_date)
        assert result.weekday() == 0  # Monday

        result = parse_natural("next monday", reference=ref_date)
        assert result.weekday() == 0
        assert result.date() == (ref_date + timedelta(days=7)).date()

        result = parse_natural("last monday", reference=ref_date)
        assert result.weekday() == 0
        assert result.date() == (ref_date - timedelta(days=7)).date()

    def test_parse_relative_time(self) -> None:
        """Test parsing relative time expressions."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Time expressions
        result = parse_natural("now", reference=ref_date)
        assert result == ref_date

        result = parse_natural("in 1 hour", reference=ref_date)
        assert result == ref_date + timedelta(hours=1)

        result = parse_natural("in 30 minutes", reference=ref_date)
        assert result == ref_date + timedelta(minutes=30)

        result = parse_natural("2 hours ago", reference=ref_date)
        assert result == ref_date - timedelta(hours=2)

        result = parse_natural("5 minutes ago", reference=ref_date)
        assert result == ref_date - timedelta(minutes=5)

    def test_parse_specific_times(self) -> None:
        """Test parsing specific time expressions."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Specific times today
        result = parse_natural("9am", reference=ref_date)
        assert result.time() == datetime(2024, 7, 15, 9, 0, 0).time()

        result = parse_natural("2:30pm", reference=ref_date)
        assert result.time() == datetime(2024, 7, 15, 14, 30, 0).time()

        result = parse_natural("noon", reference=ref_date)
        assert result.time() == datetime(2024, 7, 15, 12, 0, 0).time()

        result = parse_natural("midnight", reference=ref_date)
        assert result.time() == datetime(2024, 7, 15, 0, 0, 0).time()

        # Specific times with day references
        result = parse_natural("tomorrow at 9am", reference=ref_date)
        expected = ref_date + timedelta(days=1)
        expected = expected.replace(hour=9, minute=0, second=0, microsecond=0)
        assert result == expected

        result = parse_natural("monday at 2:30pm", reference=ref_date)
        # Should be today (Monday) at 2:30pm
        expected = ref_date.replace(hour=14, minute=30, second=0, microsecond=0)
        assert result == expected

    def test_parse_complex_expressions(self) -> None:
        """Test parsing complex natural language expressions."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Complex relative expressions
        result = parse_natural("next week", reference=ref_date)
        assert result.date() == (ref_date + timedelta(weeks=1)).date()

        result = parse_natural("last week", reference=ref_date)
        assert result.date() == (ref_date - timedelta(weeks=1)).date()

        result = parse_natural("in 2 days", reference=ref_date)
        assert result.date() == (ref_date + timedelta(days=2)).date()

        result = parse_natural("3 days ago", reference=ref_date)
        assert result.date() == (ref_date - timedelta(days=3)).date()

        # Month/year expressions
        result = parse_natural("next month", reference=ref_date)
        assert result.month == 8  # August
        assert result.year == 2024

        result = parse_natural("last month", reference=ref_date)
        assert result.month == 6  # June
        assert result.year == 2024

    def test_parse_with_timezone(self) -> None:
        """Test parsing with timezone awareness."""
        from time_helper import parse_natural

        ref_date = make_aware("2024-07-15 12:00:00", "America/New_York")

        # Parse with timezone context
        result = parse_natural("tomorrow at 9am", reference=ref_date)
        assert result.tzinfo == ref_date.tzinfo

        # Parse with explicit timezone
        result = parse_natural("tomorrow at 9am EST", reference=ref_date)
        assert result.tzinfo is not None

    def test_parse_edge_cases(self) -> None:
        """Test edge cases and error handling."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Invalid expressions should raise ValueError
        with pytest.raises(ValueError):
            parse_natural("invalid expression", reference=ref_date)

        with pytest.raises(ValueError):
            parse_natural("", reference=ref_date)

        # Case insensitive
        result = parse_natural("TODAY", reference=ref_date)
        assert result.date() == ref_date.date()

        result = parse_natural("Tomorrow", reference=ref_date)
        assert result.date() == (ref_date + timedelta(days=1)).date()

    def test_parse_weekend_references(self) -> None:
        """Test parsing weekend-specific references."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Weekend references
        result = parse_natural("this weekend", reference=ref_date)
        assert result.weekday() == 5  # Saturday

        result = parse_natural("next weekend", reference=ref_date)
        assert result.weekday() == 5  # Saturday
        assert result.date() == (ref_date + timedelta(days=12)).date()

        result = parse_natural("last weekend", reference=ref_date)
        assert result.weekday() == 5  # Saturday
        assert result.date() == (ref_date - timedelta(days=2)).date()

    def test_parse_with_default_reference(self) -> None:
        """Test parsing without explicit reference (should use current time)."""
        from time_helper import parse_natural

        # Should use current time as reference
        result = parse_natural("now")
        assert result is not None
        assert isinstance(result, datetime)

        # Should be close to current time (within 5 seconds)
        now = datetime.now()
        diff = abs((result - now).total_seconds())
        assert diff < 5.0

    def test_parse_seasonal_references(self) -> None:
        """Test parsing seasonal and holiday references."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Season references (approximate)
        result = parse_natural("beginning of year", reference=ref_date)
        assert result.month == 1
        assert result.day == 1

        result = parse_natural("end of year", reference=ref_date)
        assert result.month == 12
        assert result.day == 31

        result = parse_natural("beginning of month", reference=ref_date)
        assert result.month == 7
        assert result.day == 1

        result = parse_natural("end of month", reference=ref_date)
        assert result.month == 7
        assert result.day == 31


class TestNaturalLanguageWithDateTimeWrapper:
    """Test natural language parsing with DateTimeWrapper integration."""

    def test_wrapper_parse_natural(self) -> None:
        """Test DateTimeWrapper can parse natural language."""
        from time_helper import DateTimeWrapper

        # DateTimeWrapper should support natural language parsing
        # Create wrapper with natural language
        dtw = DateTimeWrapper("tomorrow")
        assert dtw.dt is not None
        # Note: without reference, it uses current time

        # Chain operations
        result = DateTimeWrapper("tomorrow at 9am").make_aware("UTC").round("H")
        assert result.dt is not None
        assert result.dt.hour == 9

    def test_wrapper_natural_language_methods(self) -> None:
        """Test DateTimeWrapper methods that could use natural language."""
        from time_helper import DateTimeWrapper

        ref_date = datetime(2024, 7, 15, 12, 0, 0)
        dtw = DateTimeWrapper(ref_date)

        # Method that could parse natural language offsets
        # Note: These methods don't exist yet, this is TDD
        tomorrow = dtw.add_natural("1 day")  # type: ignore[attr-defined]
        assert tomorrow.dt is not None
        assert tomorrow.dt.date() == (ref_date + timedelta(days=1)).date()

        next_week = dtw.add_natural("1 week")  # type: ignore[attr-defined]
        assert next_week.dt is not None
        assert next_week.dt.date() == (ref_date + timedelta(weeks=1)).date()


class TestNaturalLanguageFormats:
    """Test various natural language formats and patterns."""

    def test_ordinal_dates(self) -> None:
        """Test ordinal date expressions."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Ordinal expressions
        result = parse_natural("first of the month", reference=ref_date)
        assert result.day == 1
        assert result.month == 7

        result = parse_natural("last day of the month", reference=ref_date)
        assert result.day == 31
        assert result.month == 7

        result = parse_natural("15th of next month", reference=ref_date)
        assert result.day == 15
        assert result.month == 8

    def test_business_day_references(self) -> None:
        """Test business day references."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday

        # Business day references
        result = parse_natural("next business day", reference=ref_date)
        assert result.weekday() == 1  # Tuesday

        # From Friday
        friday = datetime(2024, 7, 19, 12, 0, 0)
        result = parse_natural("next business day", reference=friday)
        assert result.weekday() == 0  # Monday

        result = parse_natural("last business day", reference=ref_date)
        assert result.weekday() == 4  # Friday (previous week)

    def test_time_ranges(self) -> None:
        """Test time range expressions."""
        from time_helper import parse_natural

        ref_date = datetime(2024, 7, 15, 12, 0, 0)

        # Time ranges
        result = parse_natural("morning", reference=ref_date)
        assert 6 <= result.hour <= 11

        result = parse_natural("afternoon", reference=ref_date)
        assert 12 <= result.hour <= 17

        result = parse_natural("evening", reference=ref_date)
        assert 18 <= result.hour <= 21

        result = parse_natural("night", reference=ref_date)
        assert result.hour >= 22 or result.hour <= 5


def test_ordinal_next_month_december() -> None:
    """Test ordinal date pattern with 'next month' in December."""
    # This tests line 263 - the December edge case for "15th of next month"
    ref_date = datetime(2024, 12, 10, 12, 0, 0)

    result = parse_natural("15th of next month", reference=ref_date)
    assert result.year == 2025
    assert result.month == 1
    assert result.day == 15
    assert result.hour == 0
    assert result.minute == 0
