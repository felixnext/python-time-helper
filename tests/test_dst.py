"""Additional tests for DST module to improve coverage."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from time_helper import (
    DateTimeWrapper,
    get_dst_transitions,
    is_dst_active,
    localize_datetime,
    make_aware,
    next_dst_transition,
    parse_time,
    round_time,
    time_diff,
)


class TestDSTTransitions:
    """Test handling of DST transitions for various timezones."""

    def test_cet_to_cest_spring_transition(self) -> None:
        """Test CET to CEST transition (spring forward)."""
        # In 2024, CET->CEST transition happens on March 31 at 2:00 AM
        # Clock jumps from 01:59:59 CET to 03:00:00 CEST
        tz = ZoneInfo("Europe/Berlin")

        # Just before transition (1:30 AM CET)
        dt_before = datetime(2024, 3, 31, 1, 30, tzinfo=tz)
        assert dt_before.dst() == timedelta(0)
        assert dt_before.tzname() == "CET"

        # Non-existent time (2:30 AM doesn't exist)
        # ZoneInfo handles this by adjusting forward
        dt_nonexistent = datetime(2024, 3, 31, 2, 30, tzinfo=tz)
        # The time is kept but it's in standard time
        assert dt_nonexistent.hour == 2
        assert dt_nonexistent.dst() == timedelta(0)  # Still CET

        # After transition (3:30 AM CEST)
        dt_after = datetime(2024, 3, 31, 3, 30, tzinfo=tz)
        assert dt_after.dst() == timedelta(hours=1)
        assert dt_after.tzname() == "CEST"

    def test_cest_to_cet_fall_transition(self) -> None:
        """Test CEST to CET transition (fall back)."""
        # In 2024, CEST->CET transition happens on October 27 at 3:00 AM
        # Clock jumps back from 02:59:59 CEST to 02:00:00 CET
        tz = ZoneInfo("Europe/Berlin")

        # Before transition (1:30 AM CEST)
        dt_before = datetime(2024, 10, 27, 1, 30, tzinfo=tz)
        assert dt_before.dst() == timedelta(hours=1)
        assert dt_before.tzname() == "CEST"

        # Ambiguous time (2:30 AM exists twice)
        # First occurrence (CEST)
        dt_ambig_cest = datetime(2024, 10, 27, 2, 30, tzinfo=tz, fold=0)
        assert dt_ambig_cest.dst() == timedelta(hours=1)
        assert dt_ambig_cest.tzname() == "CEST"

        # Second occurrence (CET)
        dt_ambig_cet = datetime(2024, 10, 27, 2, 30, tzinfo=tz, fold=1)
        assert dt_ambig_cet.dst() == timedelta(0)
        assert dt_ambig_cet.tzname() == "CET"

        # After transition (3:30 AM CET)
        dt_after = datetime(2024, 10, 27, 3, 30, tzinfo=tz)
        assert dt_after.dst() == timedelta(0)
        assert dt_after.tzname() == "CET"

    def test_multiple_timezone_dst_transitions(self) -> None:
        """Test DST transitions across different timezone systems."""
        test_cases = [
            # (timezone, spring_date, fall_date)
            ("Europe/London", datetime(2024, 3, 31), datetime(2024, 10, 27)),
            ("America/New_York", datetime(2024, 3, 10), datetime(2024, 11, 3)),
            ("Australia/Sydney", datetime(2024, 10, 6), datetime(2024, 4, 7)),  # Southern hemisphere
        ]

        for tz_name, spring_date, fall_date in test_cases:
            tz = ZoneInfo(tz_name)

            # Test spring forward
            dt_before_spring = spring_date.replace(hour=1, minute=30, tzinfo=tz)
            dt_after_spring = spring_date.replace(hour=3, minute=30, tzinfo=tz)
            assert (dt_after_spring.dst() or timedelta(0)) > (dt_before_spring.dst() or timedelta(0))

            # Test fall back
            dt_before_fall = fall_date.replace(hour=1, minute=30, tzinfo=tz)
            dt_after_fall = fall_date.replace(hour=3, minute=30, tzinfo=tz)
            # In fall, DST should decrease or stay the same
            assert (dt_after_fall.dst() or timedelta(0)) <= (dt_before_fall.dst() or timedelta(0))


class TestDSTAwareDateTimeOperations:
    """Test datetime operations with DST awareness."""

    def test_time_diff_across_dst_boundary(self) -> None:
        """Test time_diff correctly handles DST transitions."""
        # Create two datetimes 24 hours apart, crossing DST boundary
        dt1 = make_aware("2024-03-30 12:00:00", "Europe/Berlin")
        dt2 = make_aware("2024-03-31 12:00:00", "Europe/Berlin")  # After DST transition

        # Even though wall clock shows same time, actual diff is 23 hours
        diff = time_diff(dt2, dt1)
        assert diff == timedelta(hours=23)  # Lost 1 hour due to DST

    def test_round_time_during_dst_transition(self) -> None:
        """Test round_time behavior during DST transitions."""
        # Round a time during the non-existent hour
        dt = make_aware("2024-03-31 02:30:00", "Europe/Berlin")

        # Round to hour
        rounded_hour = round_time(dt, "H")
        assert rounded_hour is not None
        assert rounded_hour.hour == 2
        assert rounded_hour.minute == 0

        # Round to day
        rounded_day = round_time(dt, "D")
        assert rounded_day is not None
        assert rounded_day.hour == 0
        assert rounded_day.day == 31

    def test_localize_datetime_with_ambiguous_times(self) -> None:
        """Test localizing datetime during ambiguous DST times."""
        # Create naive datetime during fall-back hour
        naive_dt = datetime(2024, 10, 27, 2, 30)

        # Localize to Berlin time
        localized = localize_datetime(naive_dt, "Europe/Berlin")
        assert localized is not None
        assert localized.tzinfo is not None

        # By default, it should choose the first occurrence (DST)
        assert localized.fold == 0
        assert localized.dst() == timedelta(hours=1)

    def test_parsing_dst_aware_strings(self) -> None:
        """Test parsing datetime strings with DST information."""
        # Parse time with timezone that observes DST
        dt = parse_time("2024-07-15 14:30:00", "%Y-%m-%d %H:%M:%S", "Europe/Berlin")
        assert dt is not None
        assert dt.dst() == timedelta(hours=1)  # Summer time
        assert dt.tzname() == "CEST"

        # Parse winter time
        dt_winter = parse_time("2024-01-15 14:30:00", "%Y-%m-%d %H:%M:%S", "Europe/Berlin")
        assert dt_winter is not None
        assert dt_winter.dst() == timedelta(0)  # Standard time
        assert dt_winter.tzname() == "CET"


class TestDSTEdgeCases:
    """Test edge cases and potential issues with DST."""

    def test_repeated_hour_during_fall_back(self) -> None:
        """Test handling of the repeated hour during fall-back."""
        tz = ZoneInfo("Europe/Berlin")

        # Create times during the repeated hour
        # In fall back, 2:00-3:00 occurs twice
        # fold=0 is the first occurrence (CEST, UTC+2)
        # fold=1 is the second occurrence (CET, UTC+1)

        # First occurrence at 2:00 CEST
        dt1_cest = datetime(2024, 10, 27, 2, 0, tzinfo=tz, fold=0)
        assert dt1_cest.tzname() == "CEST"

        # Second occurrence at 2:00 CET (1 hour later in real time)
        dt2_cet = datetime(2024, 10, 27, 2, 0, tzinfo=tz, fold=1)
        assert dt2_cet.tzname() == "CET"

        # The CET time (fold=1) is actually later than CEST time (fold=0)
        assert dt2_cet.timestamp() > dt1_cest.timestamp()

        # Difference should be 1 hour
        diff = dt2_cet.timestamp() - dt1_cest.timestamp()
        assert diff == 3600  # 1 hour in seconds

    def test_datetime_arithmetic_across_dst(self) -> None:
        """Test datetime arithmetic across DST boundaries."""
        # Start just before spring DST transition
        dt = make_aware("2024-03-30 23:00:00", "Europe/Berlin")

        # Add 4 hours - crosses DST boundary
        result = dt + timedelta(hours=4)

        # Wall clock should show 3:00 AM (arithmetic is correct, DST doesn't affect it)
        assert result.hour == 3  # 23:00 + 4 hours = 03:00
        assert result.day == 31

        # Actual elapsed time is still 4 hours
        diff = result - dt
        assert diff == timedelta(hours=4)

    def test_dst_transition_in_different_years(self) -> None:
        """Test that DST transitions are handled correctly across years."""
        years = [2023, 2024, 2025]
        tz = ZoneInfo("Europe/Berlin")

        for year in years:
            # Find approximate DST transition dates
            # Spring: last Sunday of March
            # Fall: last Sunday of October

            # Test summer time
            summer = datetime(year, 7, 15, 12, 0, tzinfo=tz)
            assert summer.dst() == timedelta(hours=1)
            assert summer.tzname() == "CEST"

            # Test winter time
            winter = datetime(year, 1, 15, 12, 0, tzinfo=tz)
            assert winter.dst() == timedelta(0)
            assert winter.tzname() == "CET"


class TestDateTimeWrapperDST:
    """Test DateTimeWrapper with DST support."""

    def test_wrapper_preserves_dst_info(self) -> None:
        """Test that DateTimeWrapper preserves DST information."""
        # Create wrapper with summer time
        summer = DateTimeWrapper("2024-07-15 14:30:00").make_aware("Europe/Berlin")
        assert summer.dt is not None
        assert summer.dt.dst() == timedelta(hours=1)
        assert summer.dt.tzname() == "CEST"

        # Create wrapper with winter time
        winter = DateTimeWrapper("2024-01-15 14:30:00").make_aware("Europe/Berlin")
        assert winter.dt is not None
        assert winter.dt.dst() == timedelta(0)
        assert winter.dt.tzname() == "CET"

    def test_wrapper_operations_across_dst(self) -> None:
        """Test DateTimeWrapper operations across DST boundaries."""
        # Start before DST transition
        dtw = DateTimeWrapper("2024-03-30 23:00:00").make_aware("Europe/Berlin")

        # Add time across DST boundary
        result = dtw + timedelta(hours=4)
        assert result.dt is not None
        assert result.dt.hour == 3  # Regular arithmetic, DST doesn't change it

        # Chain operations
        # Start at 1:00 AM on Oct 27 (before DST transition)
        chained = (
            DateTimeWrapper("2024-10-27 01:00:00")
            .make_aware("Europe/Berlin")
            .localize("UTC")  # Convert to UTC to avoid ambiguity
            .round("D")  # This rounds to midnight UTC
            .localize("Europe/Berlin")
        )  # Convert back to Berlin time

        assert chained.dt is not None
        # Midnight UTC on Oct 27 is 2:00 AM in Berlin (CEST)
        assert chained.dt.hour == 2
        assert chained.dt.day == 26  # Actually Oct 26 in Berlin time

    def test_wrapper_string_representation_with_dst(self) -> None:
        """Test string representation includes DST info."""
        dtw = DateTimeWrapper("2024-07-15 14:30:00").make_aware("Europe/Berlin")

        # Custom format with timezone name
        tz_str = dtw.to_string("%Y-%m-%d %H:%M:%S %Z")
        assert "CEST" in tz_str

        # ISO format
        iso_str = str(dtw)
        assert "14:30:00" in iso_str


class TestDSTHelperFunctions:
    """Test helper functions for DST support."""

    def test_is_dst_active(self) -> None:
        """Test checking if DST is currently active."""
        # Note: This is a proposed function that doesn't exist yet
        # We're writing the test first (TDD)
        from time_helper import is_dst_active

        # Summer time in Berlin
        summer = make_aware("2024-07-15 12:00:00", "Europe/Berlin")
        assert is_dst_active(summer) is True

        # Winter time in Berlin
        winter = make_aware("2024-01-15 12:00:00", "Europe/Berlin")
        assert is_dst_active(winter) is False

        # Timezone that doesn't observe DST
        no_dst = make_aware("2024-07-15 12:00:00", "Asia/Tokyo")
        assert is_dst_active(no_dst) is False

    def test_get_dst_transitions(self) -> None:
        """Test getting DST transition dates for a timezone."""
        # Note: This is a proposed function that doesn't exist yet
        from time_helper import get_dst_transitions

        # Get transitions for 2024 in Berlin
        transitions = get_dst_transitions("Europe/Berlin", 2024)

        assert len(transitions) == 2
        assert transitions[0]["type"] == "spring_forward"
        assert transitions[0]["date"].month == 3
        assert transitions[1]["type"] == "fall_back"
        assert transitions[1]["date"].month == 10

    def test_next_dst_transition(self) -> None:
        """Test finding the next DST transition."""
        # Note: This is a proposed function that doesn't exist yet
        from time_helper import next_dst_transition

        # From winter, next transition is spring
        winter = make_aware("2024-02-15 12:00:00", "Europe/Berlin")
        next_trans = next_dst_transition(winter)
        assert next_trans is not None
        assert next_trans["type"] == "spring_forward"
        assert next_trans["date"].month == 3

        # From summer, next transition is fall
        summer = make_aware("2024-07-15 12:00:00", "Europe/Berlin")
        next_trans = next_dst_transition(summer)
        assert next_trans is not None
        assert next_trans["type"] == "fall_back"
        assert next_trans["date"].month == 10


class TestDSTCoverage:
    """Test error conditions and edge cases in DST functions."""

    def test_is_dst_active_error_cases(self) -> None:
        """Test error conditions for is_dst_active."""
        # Test with None datetime
        with pytest.raises(ValueError, match="Cannot check DST for None datetime"):
            is_dst_active(None)

        # Test with timezone-unaware datetime
        naive_dt = datetime(2024, 7, 15, 12, 0, 0)
        with pytest.raises(ValueError, match="Cannot check DST for timezone-unaware datetime"):
            is_dst_active(naive_dt)

    def test_get_dst_transitions_error_cases(self) -> None:
        """Test error conditions for get_dst_transitions."""
        # Test with invalid timezone string
        with pytest.raises(ValueError, match="Invalid timezone: Invalid/Timezone"):
            get_dst_transitions("Invalid/Timezone", 2024)

        # Test with timezone that doesn't observe DST
        transitions = get_dst_transitions("UTC", 2024)
        assert len(transitions) == 0

        # Test with Asia/Tokyo (no DST)
        transitions = get_dst_transitions("Asia/Tokyo", 2024)
        assert len(transitions) == 0

        # Test with direct ZoneInfo object
        tz = ZoneInfo("Europe/Berlin")
        transitions = get_dst_transitions(tz, 2024)
        assert len(transitions) == 2  # Should have spring and fall transitions

    def test_next_dst_transition_error_cases(self) -> None:
        """Test error conditions for next_dst_transition."""
        # Test with None datetime
        with pytest.raises(ValueError, match="Cannot find DST transition for None datetime"):
            next_dst_transition(None)  # type: ignore[arg-type]

        # Test with timezone-unaware datetime
        naive_dt = datetime(2024, 7, 15, 12, 0, 0)
        with pytest.raises(ValueError, match="Cannot find DST transition for timezone-unaware datetime"):
            next_dst_transition(naive_dt)

        # Test with non-ZoneInfo timezone
        utc_dt = datetime(2024, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="DST transitions only supported for ZoneInfo timezones"):
            next_dst_transition(utc_dt)

    def test_dst_transition_edge_cases(self) -> None:
        """Test edge cases in DST transition detection."""
        # Test with timezone that has complex DST rules
        ZoneInfo("America/New_York")

        # Test near end of year (should look to next year)
        late_dt = make_aware("2024-12-15 12:00:00", "America/New_York")
        next_trans = next_dst_transition(late_dt)
        assert next_trans is not None
        assert next_trans["type"] == "spring_forward"
        assert next_trans["date"].year == 2025

    def test_dst_transition_no_more_transitions(self) -> None:
        """Test case where no more DST transitions exist."""
        # Test with timezone that doesn't have DST
        tokyo_dt = make_aware("2024-07-15 12:00:00", "Asia/Tokyo")
        next_trans = next_dst_transition(tokyo_dt)
        assert next_trans is None

    def test_dst_transition_spring_forward_exception_handling(self) -> None:
        """Test exception handling during spring forward transition."""
        # This is harder to test directly, but we can test the transition detection
        # for a timezone that has spring forward
        tz = ZoneInfo("Europe/Berlin")
        transitions = get_dst_transitions(tz, 2024)

        # Should have 2 transitions
        assert len(transitions) == 2

        # First should be spring forward
        spring_trans = transitions[0]
        assert spring_trans["type"] == "spring_forward"
        assert spring_trans["date"].month == 3

        # Second should be fall back
        fall_trans = transitions[1]
        assert fall_trans["type"] == "fall_back"
        assert fall_trans["date"].month == 10

    def test_dst_invalid_date_handling(self) -> None:
        """Test handling of invalid dates during DST transition detection."""
        # Test with a year that might have unusual calendar behavior
        # The function should handle invalid dates gracefully
        transitions = get_dst_transitions("Europe/Berlin", 2024)

        # Should still work normally
        assert len(transitions) == 2

        # Test with a very early year (might cause issues)
        transitions = get_dst_transitions("Europe/Berlin", 1970)
        # Should not crash, even if no transitions found
        assert isinstance(transitions, list)

    def test_dst_transition_boundary_conditions(self) -> None:
        """Test boundary conditions for DST transitions."""
        # Test very close to DST transition
        ZoneInfo("America/New_York")

        # Just before spring forward 2024 (March 10)
        before_spring = make_aware("2024-03-09 12:00:00", "America/New_York")
        assert not is_dst_active(before_spring)

        # Just after spring forward
        after_spring = make_aware("2024-03-11 12:00:00", "America/New_York")
        assert is_dst_active(after_spring)

        # Just before fall back 2024 (November 3)
        before_fall = make_aware("2024-11-02 12:00:00", "America/New_York")
        assert is_dst_active(before_fall)

        # Just after fall back
        after_fall = make_aware("2024-11-04 12:00:00", "America/New_York")
        assert not is_dst_active(after_fall)

    def test_dst_with_different_timezone_formats(self) -> None:
        """Test DST functions with different timezone input formats."""
        # Test with string timezone
        transitions_str = get_dst_transitions("Europe/Berlin", 2024)

        # Test with ZoneInfo object
        tz = ZoneInfo("Europe/Berlin")
        transitions_zi = get_dst_transitions(tz, 2024)

        # Should be the same
        assert len(transitions_str) == len(transitions_zi)
        assert transitions_str[0]["type"] == transitions_zi[0]["type"]
        assert transitions_str[1]["type"] == transitions_zi[1]["type"]

    def test_dst_leap_year_handling(self) -> None:
        """Test DST transition detection in leap years."""
        # Test leap year
        transitions_leap = get_dst_transitions("Europe/Berlin", 2024)  # 2024 is leap year

        # Test non-leap year
        transitions_normal = get_dst_transitions("Europe/Berlin", 2023)  # 2023 is not leap year

        # Both should have 2 transitions
        assert len(transitions_leap) == 2
        assert len(transitions_normal) == 2

        # Transitions should be same type
        assert transitions_leap[0]["type"] == transitions_normal[0]["type"]
        assert transitions_leap[1]["type"] == transitions_normal[1]["type"]
