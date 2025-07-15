"""Comprehensive timezone tests to ensure robustness across all timezone scenarios."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from time_helper import any_to_datetime, current_timezone, find_timezone, parse_time
from time_helper.convert import localize_datetime, unix_to_datetime
from time_helper.ops import round_time
from time_helper.timezone import IANA_MAPPING


class TestTimezoneAbbreviations:
    """Test handling of ambiguous timezone abbreviations."""

    def test_ist_disambiguation(self) -> None:
        """Test that IST is properly disambiguated.

        IST can mean:
        - Indian Standard Time (UTC+5:30)
        - Irish Standard Time (UTC+1)
        - Israel Standard Time (UTC+2)

        Our mapping chooses Indian Standard Time as most common.
        """
        tz = find_timezone("IST")
        assert tz is not None
        assert str(tz) == "Asia/Kolkata"

        # Verify it's really Indian Standard Time (UTC+5:30)
        dt = datetime(2023, 6, 15, 12, 0, tzinfo=tz)
        utc_offset = dt.utcoffset()
        assert utc_offset == timedelta(hours=5, minutes=30)

    def test_cst_disambiguation(self) -> None:
        """Test CST disambiguation.

        CST can mean:
        - Central Standard Time (US) UTC-6
        - China Standard Time UTC+8
        - Cuba Standard Time UTC-5
        """
        tz = find_timezone("CST")
        assert tz is not None
        assert str(tz) == "America/Chicago"

        # Verify it's US Central time
        dt = datetime(2023, 1, 15, 12, 0, tzinfo=tz)  # Winter - no DST
        utc_offset = dt.utcoffset()
        assert utc_offset == timedelta(hours=-6)

    def test_bst_disambiguation(self) -> None:
        """Test BST disambiguation.

        BST can mean:
        - British Summer Time UTC+1
        - Bangladesh Standard Time UTC+6
        - Bougainville Standard Time UTC+11
        """
        tz = find_timezone("BST")
        assert tz is not None
        assert str(tz) == "Europe/London"

        # BST is British Summer Time, so test during summer
        dt = datetime(2023, 7, 15, 12, 0, tzinfo=tz)
        utc_offset = dt.utcoffset()
        assert utc_offset == timedelta(hours=1)

    def test_all_mapped_abbreviations(self) -> None:
        """Test all abbreviations in IANA_MAPPING are valid."""
        for abbr, full_tz in IANA_MAPPING.items():
            tz = find_timezone(abbr)
            assert tz is not None, f"Failed to find timezone for {abbr}"
            assert str(tz) == full_tz, f"Wrong mapping for {abbr}: expected {full_tz}, got {tz!s}"


class TestTimezoneFormats:
    """Test various timezone format inputs."""

    def test_full_iana_names(self) -> None:
        """Test full IANA timezone names."""
        test_cases = [
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
            "Australia/Sydney",
            "Africa/Cairo",
            "America/Argentina/Buenos_Aires",  # Multi-level
            "Pacific/Auckland",
            "UTC",
            "GMT",
        ]

        for tz_name in test_cases:
            tz = find_timezone(tz_name)
            assert tz is not None, f"Failed to find {tz_name}"
            assert str(tz) == tz_name

    def test_case_sensitivity(self) -> None:
        """Test that timezone lookups handle case properly."""
        # Abbreviations are case-sensitive in our mapping
        assert find_timezone("ist") is None  # Not in mapping (lowercase)
        assert find_timezone("IST") is not None  # In mapping (uppercase)

        # ZoneInfo accepts both cases for some timezones but we should use proper case
        # Both might work but proper case is recommended
        find_timezone("america/new_york")
        tz_proper = find_timezone("America/New_York")
        assert tz_proper is not None

    def test_invalid_timezones(self) -> None:
        """Test handling of invalid timezone names."""
        invalid = [
            "Invalid/Timezone",
            "XYZ",  # Not in mapping
            "America/InvalidCity",
            "",
            "   ",  # Whitespace
        ]

        for tz_name in invalid:
            tz = find_timezone(tz_name)
            assert tz is None, f"Expected None for invalid timezone {tz_name}"

    def test_tzinfo_passthrough(self) -> None:
        """Test that tzinfo objects are passed through unchanged."""
        original_tz = ZoneInfo("America/New_York")
        result = find_timezone(original_tz)
        assert result is original_tz


class TestTimezoneParsing:
    """Test timezone handling in parsing functions."""

    def test_parse_time_with_abbreviations(self) -> None:
        """Test parse_time with timezone abbreviations."""
        time_str = "2023-06-15 12:00:00"
        format_str = "%Y-%m-%d %H:%M:%S"

        # Test with IST abbreviation
        dt = parse_time(time_str, format_str, "IST")
        assert dt is not None
        assert dt.tzinfo is not None
        assert str(dt.tzinfo) == "Asia/Kolkata"

    def test_parse_time_with_full_names(self) -> None:
        """Test parse_time with full timezone names."""
        time_str = "2023-06-15 12:00:00"
        format_str = "%Y-%m-%d %H:%M:%S"

        dt = parse_time(time_str, format_str, "America/New_York")
        assert dt is not None
        assert dt.tzinfo is not None
        assert str(dt.tzinfo) == "America/New_York"

    def test_any_to_datetime_with_timezone_suffix(self) -> None:
        """Test parsing datetime strings with timezone information."""
        test_cases = [
            # ISO format with Z (UTC)
            ("2023-06-15T12:00:00Z", "UTC", 0),
            # With timezone offset
            ("2023-06-15T12:00:00+05:30", None, 5.5),  # IST offset
            ("2023-06-15T12:00:00-05:00", None, -5),  # EST offset
            ("2023-06-15T12:00:00+09:00", None, 9),  # JST offset
        ]

        for dt_str, expected_tz, expected_offset_hours in test_cases:
            dt = any_to_datetime(dt_str)
            assert dt is not None
            assert dt.tzinfo is not None

            if expected_tz:
                # For Z suffix, we might get UTC or timezone.utc
                assert "UTC" in str(dt.tzinfo).upper() or "utc" in str(dt.tzinfo)

            if expected_offset_hours is not None:
                offset = dt.utcoffset()
                assert offset == timedelta(hours=expected_offset_hours)

    def test_unix_timestamp_timezone_handling(self) -> None:
        """Test unix timestamp conversion with different timezones."""
        timestamp = 1686830400  # 2023-06-15 12:00:00 UTC

        # Default (UTC)
        dt_utc = unix_to_datetime(timestamp)
        assert dt_utc.hour == 12
        assert dt_utc.tzinfo is not None

        # With specific timezone
        dt_ny = unix_to_datetime(timestamp, tz="America/New_York")
        assert dt_ny.hour == 8  # UTC-4 in summer
        assert str(dt_ny.tzinfo) == "America/New_York"

        # With abbreviation
        dt_ist = unix_to_datetime(timestamp, tz="IST")
        assert dt_ist.hour == 17  # UTC+5:30
        assert dt_ist.minute == 30
        assert str(dt_ist.tzinfo) == "Asia/Kolkata"


class TestTimezoneDST:
    """Test Daylight Saving Time transitions."""

    def test_dst_transition_spring_forward(self) -> None:
        """Test handling of spring DST transition (2AM -> 3AM)."""
        # US DST starts second Sunday in March
        # In 2023, that's March 12
        tz = find_timezone("America/New_York")

        # 1:30 AM exists - standard time
        dt_before = datetime(2023, 3, 12, 1, 30, tzinfo=tz)
        assert dt_before.dst() == timedelta(0)

        # 2:30 AM doesn't exist (skipped hour) but ZoneInfo handles it
        # It keeps the time but treats it as standard time (pre-DST)
        dt_skip = datetime(2023, 3, 12, 2, 30, tzinfo=tz)
        assert dt_skip.hour == 2
        assert dt_skip.dst() == timedelta(0)  # Still standard time

        # 3:30 AM is after transition - DST active
        dt_after = datetime(2023, 3, 12, 3, 30, tzinfo=tz)
        assert dt_after.hour == 3
        assert dt_after.dst() == timedelta(hours=1)  # DST active

    def test_dst_transition_fall_back(self) -> None:
        """Test handling of fall DST transition (2AM -> 1AM)."""
        # US DST ends first Sunday in November
        # In 2023, that's November 5
        tz = find_timezone("America/New_York")

        # 1:30 AM occurs twice - this is ambiguous
        # Most libraries will default to one or the other
        dt = datetime(2023, 11, 5, 1, 30, tzinfo=tz)
        assert dt.tzinfo is not None

    def test_operations_across_dst(self) -> None:
        """Test datetime operations across DST boundaries."""
        tz = find_timezone("America/New_York")

        # Start before DST transition
        dt_before = localize_datetime(datetime(2023, 3, 11, 12, 0), tz)
        assert dt_before is not None

        # Add 24 hours - crosses DST boundary
        dt_after = dt_before + timedelta(hours=24)

        # timedelta arithmetic preserves absolute time, not wall clock
        # So 24 hours later is still 12:00 PM (but now in DST)
        assert dt_after.hour == 12
        assert dt_after.day == 12

        # Verify DST changed
        assert dt_before.dst() == timedelta(0)  # No DST
        assert dt_after.dst() == timedelta(hours=1)  # DST active

        # It's exactly 24 hours later in absolute time
        diff = dt_after - dt_before
        assert diff == timedelta(hours=24)


class TestTimezoneOperations:
    """Test timezone-aware operations."""

    def test_round_time_preserves_timezone(self) -> None:
        """Test that round_time preserves timezone information."""
        tz = find_timezone("America/New_York")
        dt = localize_datetime(datetime(2023, 6, 15, 12, 35, 42), tz)
        assert dt is not None

        # Round to hour (use "H" not "hour")
        rounded = round_time(dt, "H")
        assert rounded is not None
        assert rounded.tzinfo is not None
        assert str(rounded.tzinfo) == "America/New_York"
        assert rounded.hour == 12  # Same hour, minutes/seconds zeroed
        assert rounded.minute == 0
        assert rounded.second == 0

        # Round to day
        rounded = round_time(dt, "D")
        assert rounded is not None
        assert rounded.tzinfo is not None
        assert str(rounded.tzinfo) == "America/New_York"
        assert rounded.hour == 0
        assert rounded.day == 15  # Same day, time zeroed

    def test_timedelta_preserves_timezone(self) -> None:
        """Test that timedelta operations preserve timezone."""
        tz = find_timezone("Asia/Tokyo")
        dt = localize_datetime(datetime(2023, 6, 15, 12, 0), tz)
        assert dt is not None

        # Add hours
        shifted = dt + timedelta(hours=3)
        assert shifted.tzinfo is not None
        assert str(shifted.tzinfo) == "Asia/Tokyo"
        assert shifted.hour == 15

        # Add days
        shifted = dt + timedelta(days=1)
        assert shifted.tzinfo is not None
        assert str(shifted.tzinfo) == "Asia/Tokyo"
        assert shifted.day == 16

    def test_timezone_conversion(self) -> None:
        """Test converting between timezones."""
        # Create datetime in one timezone
        tz_ny = find_timezone("America/New_York")
        dt_ny = localize_datetime(datetime(2023, 6, 15, 12, 0), tz_ny)
        assert dt_ny is not None

        # Convert to another timezone
        tz_tokyo = find_timezone("Asia/Tokyo")
        dt_tokyo = dt_ny.astimezone(tz_tokyo)

        # Should be next day in Tokyo (13 hour difference in summer)
        assert dt_tokyo.day == 16
        assert dt_tokyo.hour == 1

        # But same absolute moment
        assert dt_ny.timestamp() == dt_tokyo.timestamp()


class TestTimezoneEdgeCases:
    """Test edge cases and special scenarios."""

    def test_current_timezone_abbreviation_handling(self) -> None:
        """Test that current_timezone returns proper timezone, not abbreviation."""
        tz = current_timezone()
        tz_str = str(tz)

        # Should not be just an abbreviation
        assert len(tz_str) > 3 or tz_str in ["UTC", "GMT"]

        # Should be a valid timezone we can use
        dt = datetime.now(tz)
        assert dt.tzinfo is not None

    def test_empty_and_none_handling(self) -> None:
        """Test handling of None and empty timezone inputs."""
        assert find_timezone(None) is None  # type: ignore[arg-type]
        assert find_timezone("") is None

        # But UTC should work
        assert find_timezone("UTC") is not None

    def test_historical_timezone_data(self) -> None:
        """Test that historical timezone data works correctly."""
        tz = find_timezone("America/New_York")

        # Historical date before standardization
        old_dt = datetime(1883, 11, 18, 12, 0, tzinfo=tz)
        assert old_dt.tzinfo is not None

        # Modern date
        new_dt = datetime(2023, 6, 15, 12, 0, tzinfo=tz)
        assert new_dt.tzinfo is not None

        # Offsets might be different due to historical changes
        # (NYC used local mean time before 1883)

    def test_timezone_with_half_hour_offset(self) -> None:
        """Test timezones with non-hour offsets."""
        # India: UTC+5:30
        tz_india = find_timezone("Asia/Kolkata")
        dt = datetime(2023, 6, 15, 12, 0, tzinfo=tz_india)
        offset = dt.utcoffset()
        assert offset == timedelta(hours=5, minutes=30)

        # Newfoundland: UTC-3:30 (standard) or UTC-2:30 (DST)
        tz_nf = find_timezone("America/St_Johns")
        if tz_nf:  # Might not be available on all systems
            dt = datetime(2023, 1, 15, 12, 0, tzinfo=tz_nf)
            offset = dt.utcoffset()
            assert offset == timedelta(hours=-3, minutes=-30)

    def test_timezone_with_45_minute_offset(self) -> None:
        """Test timezones with 45-minute offsets."""
        # Nepal: UTC+5:45
        tz_nepal = find_timezone("Asia/Kathmandu")
        if tz_nepal:  # Might not be available on all systems
            dt = datetime(2023, 6, 15, 12, 0, tzinfo=tz_nepal)
            offset = dt.utcoffset()
            assert offset == timedelta(hours=5, minutes=45)


class TestTimezoneIntegration:
    """Integration tests combining multiple timezone features."""

    def test_parse_and_convert_workflow(self) -> None:
        """Test typical workflow: parse in one timezone, convert to another."""
        # Parse time in IST
        time_str = "2023-06-15 15:30:00"
        dt_ist = parse_time(time_str, "%Y-%m-%d %H:%M:%S", "IST")
        assert dt_ist is not None
        assert dt_ist.tzinfo is not None
        assert str(dt_ist.tzinfo) == "Asia/Kolkata"

        # Convert to NYC time
        tz_ny = find_timezone("America/New_York")
        dt_ny = dt_ist.astimezone(tz_ny)

        # IST is 9.5 hours ahead of EDT (summer)
        assert dt_ny.hour == 6
        assert dt_ny.minute == 0

    def test_round_across_timezones(self) -> None:
        """Test rounding operations with timezone conversions."""
        # Create time just before midnight in Tokyo
        tz_tokyo = find_timezone("Asia/Tokyo")
        dt_tokyo = localize_datetime(datetime(2023, 6, 15, 23, 45), tz_tokyo)
        assert dt_tokyo is not None

        # Round to hour - H zeroes minutes/seconds
        rounded = round_time(dt_tokyo, "H")
        assert rounded is not None
        assert rounded.day == 15  # Same day
        assert rounded.hour == 23  # Same hour
        assert rounded.minute == 0  # Minutes zeroed

        # Convert to LA time
        tz_la = find_timezone("America/Los_Angeles")
        assert tz_la is not None
        dt_la = rounded.astimezone(tz_la)
        assert dt_la.day == 15
        assert dt_la.hour == 7  # 7 AM in LA (Tokyo is 16 hours ahead in summer)

    def test_comprehensive_timezone_scenario(self) -> None:
        """Test complex scenario with multiple timezone operations."""
        # Meeting scheduled for 2 PM NYC time
        tz_ny = find_timezone("America/New_York")
        meeting_ny = localize_datetime(datetime(2023, 6, 15, 14, 0), tz_ny)
        assert meeting_ny is not None

        # Participants in different timezones
        timezones = {
            "London": "Europe/London",
            "Tokyo": "Asia/Tokyo",
            "Sydney": "Australia/Sydney",
            "Mumbai": "IST",  # Using abbreviation
        }

        results = {}
        for city, tz_name in timezones.items():
            tz = find_timezone(tz_name)
            assert tz is not None, f"Failed to find timezone for {city}"

            local_time = meeting_ny.astimezone(tz)
            results[city] = local_time

            # Verify same absolute time
            assert local_time.timestamp() == meeting_ny.timestamp()

        # Verify expected local times
        assert results["London"].hour == 19  # 7 PM
        assert results["Tokyo"].day == 16  # Next day
        assert results["Tokyo"].hour == 3  # 3 AM
        assert results["Sydney"].hour == 4  # 4 AM next day
        assert results["Mumbai"].hour == 23  # 11 PM
        assert results["Mumbai"].minute == 30  # Half-hour offset
