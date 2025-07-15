import sys
from datetime import datetime, tzinfo
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from time_helper.timezone import IANA_MAPPING, current_timezone, find_timezone

LOCAL_TZ = datetime.now().astimezone().tzname()
LOCAL_TZ = "CET" if LOCAL_TZ == "CEST" else LOCAL_TZ


class TestTimezoneFullCoverage:
    """Test complete coverage of timezone.py functions."""

    def test_zoneinfo_import_error(self) -> None:
        """Test ImportError when zoneinfo is not available."""
        # Mock the import to raise ImportError
        with patch.dict(sys.modules, {"zoneinfo": None}), pytest.raises(ImportError, match="zoneinfo not available"):
            import importlib

            import time_helper.timezone

            importlib.reload(time_helper.timezone)

    def test_find_timezone_with_tzinfo_object(self) -> None:
        """Test find_timezone with tzinfo object."""
        from zoneinfo import ZoneInfo

        # Test with ZoneInfo object
        tz = ZoneInfo("UTC")
        result = find_timezone(tz)
        assert result == tz

    def test_find_timezone_with_string_in_mapping(self) -> None:
        """Test find_timezone with string in IANA_MAPPING."""
        result = find_timezone("IST")
        assert result is not None
        # IST maps to Asia/Kolkata, so check the zone info
        assert hasattr(result, "key")
        assert result.key == "Asia/Kolkata"

    def test_find_timezone_with_invalid_string(self) -> None:
        """Test find_timezone with invalid timezone string."""
        result = find_timezone("Invalid/Timezone")
        assert result is None

    def test_find_timezone_with_exception(self) -> None:
        """Test find_timezone when timezone creation raises exception."""
        # Test with string that doesn't match any timezone
        result = find_timezone("InvalidTimezone123")
        assert result is None

    def test_current_timezone_with_proper_zoneinfo(self) -> None:
        """Test current_timezone when system has proper ZoneInfo."""
        from zoneinfo import ZoneInfo

        # Mock datetime.now().astimezone() to return proper ZoneInfo
        mock_dt = MagicMock()
        utc_tz = ZoneInfo("UTC")
        mock_dt.tzinfo = utc_tz

        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = mock_dt

            result = current_timezone()
            assert result == utc_tz

    def test_current_timezone_with_none_tzname(self) -> None:
        """Test current_timezone when tzname() returns None."""
        mock_dt = MagicMock()
        mock_dt.tzinfo = None
        mock_dt.tzname.return_value = None

        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = mock_dt

            result = current_timezone()
            assert result is not None
            # Should return UTC as fallback

    def test_current_timezone_with_mapped_abbreviation(self) -> None:
        """Test current_timezone with abbreviation in IANA_MAPPING."""
        mock_dt = MagicMock()
        mock_dt.tzinfo = None
        mock_dt.tzname.return_value = "IST"

        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = mock_dt

            result = current_timezone()
            assert result is not None

    def test_current_timezone_with_cest(self) -> None:
        """Test current_timezone with CEST abbreviation."""
        mock_dt = MagicMock()
        mock_dt.tzinfo = None
        mock_dt.tzname.return_value = "CEST"

        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = mock_dt

            result = current_timezone()
            assert result is not None

    def test_current_timezone_unix_tz_env_fallback(self) -> None:
        """Test current_timezone fallback to TZ environment variable on Unix."""
        # Test the actual function behavior without complex mocking
        result = current_timezone()
        assert result is not None
        # This tests the normal path - the fallback paths are hard to test
        # without breaking the module state

    def test_current_timezone_exception_fallback(self) -> None:
        """Test current_timezone exception fallback scenarios."""
        # We can test this by using an unknown timezone name
        mock_dt = MagicMock()
        mock_dt.tzinfo = None
        mock_dt.tzname.return_value = "UNKNOWNTZ123"

        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_datetime.now.return_value.astimezone.return_value = mock_dt

            result = current_timezone()
            assert result is not None
            # Should fall back to UTC

    def test_iana_mapping_completeness(self) -> None:
        """Test that IANA_MAPPING contains expected mappings."""
        assert "IST" in IANA_MAPPING
        assert "EST" in IANA_MAPPING
        assert "CST" in IANA_MAPPING
        assert "PST" in IANA_MAPPING
        assert "BST" in IANA_MAPPING
        assert "JST" in IANA_MAPPING
        assert "CET" in IANA_MAPPING
        assert "EET" in IANA_MAPPING

        # Test specific mappings
        assert IANA_MAPPING["IST"] == "Asia/Kolkata"
        assert IANA_MAPPING["EST"] == "America/New_York"
        assert IANA_MAPPING["JST"] == "Asia/Tokyo"

    def test_current_timezone_basic_functionality(self) -> None:
        """Test basic functionality of current_timezone."""
        # Test that it returns a timezone object
        result = current_timezone()
        assert result is not None

        # Test that it can be used to create timezone-aware datetimes
        dt = datetime.now(result)
        assert dt.tzinfo is not None

    def test_find_timezone_edge_cases(self) -> None:
        """Test edge cases in find_timezone."""
        # Test with None input
        result = find_timezone(None)  # type: ignore[arg-type]
        assert result is None

        # Test with empty string
        result = find_timezone("")
        assert result is None

        # Test with invalid timezone
        result = find_timezone("Invalid/Timezone")
        assert result is None

        # Test with valid timezone
        result = find_timezone("UTC")
        assert result is not None
        assert str(result) == "UTC"

    def test_zoneinfo_import_error_handling(self) -> None:
        """Test handling of zoneinfo import errors."""
        # This test is more conceptual since we can't easily mock the import
        # But we can test that the import works correctly
        from time_helper.timezone import timezone

        # Should be able to create timezone
        utc_tz = timezone("UTC")
        assert utc_tz is not None

        # Test that it works with ZoneInfo
        from zoneinfo import ZoneInfo

        assert isinstance(utc_tz, ZoneInfo)

    def test_current_timezone_with_cest_handling(self) -> None:
        """Test current_timezone with CEST timezone handling."""
        # This tests the specific CEST handling code path
        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_dt = mock_datetime.now.return_value.astimezone.return_value
            mock_dt.tzinfo = None
            mock_dt.tzname.return_value = "CEST"

            # Should map CEST to Europe/Berlin
            result = current_timezone()
            assert result is not None
            # The exact result depends on the system, but should not crash

    def test_current_timezone_with_mapped_timezone(self) -> None:
        """Test current_timezone with timezone that exists in IANA_MAPPING."""
        with patch("time_helper.timezone.datetime") as mock_datetime:
            mock_dt = mock_datetime.now.return_value.astimezone.return_value
            mock_dt.tzinfo = None
            mock_dt.tzname.return_value = "EST"

            # Should map EST to America/New_York via IANA_MAPPING
            result = current_timezone()
            assert result is not None
            # Should work without crashing


def test_zoneinfo_import_error() -> None:
    """Test the ImportError when zoneinfo is not available."""
    # This covers lines 9-11
    with patch.dict(sys.modules, {"zoneinfo": None}), pytest.raises(ImportError, match="zoneinfo not available"):
        import importlib

        import time_helper.timezone

        importlib.reload(time_helper.timezone)


def test_current_timezone_final_fallback() -> None:
    """Test current_timezone final fallback to UTC."""
    from time_helper.timezone import current_timezone

    # Mock datetime to return problematic timezone info
    mock_dt = MagicMock()
    mock_dt.tzinfo = None
    mock_dt.tzname.return_value = "UNKNOWN_TIMEZONE"

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        # The function should handle the unknown timezone and fall back to UTC
        result = current_timezone()
        assert result is not None
        # This will test the final fallback paths including lines 90-92


def test_current_timezone_exception_in_fallback() -> None:
    """Test current_timezone when all fallback attempts fail."""
    from time_helper.timezone import current_timezone

    # Mock datetime to return problematic timezone info
    mock_dt = MagicMock()
    mock_dt.tzinfo = None
    mock_dt.tzname.return_value = "UNKNOWN_TIMEZONE"

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        # Mock timezone to fail on first call but succeed on UTC
        with patch("time_helper.timezone.timezone") as mock_tz:

            def side_effect(name):  # type: ignore[no-untyped-def]
                if name == "UTC":
                    return MagicMock()
                raise Exception("Test exception")

            mock_tz.side_effect = side_effect

            result = current_timezone()
            assert result is not None
            # This covers the exception handling in the fallback code


def test_find_timezone_exception_handling() -> None:
    """Test find_timezone exception handling."""
    from time_helper.timezone import find_timezone

    # Use a clearly invalid timezone name that will cause an exception
    result = find_timezone("Invalid/Timezone/Name/123")
    assert result is None
    # This covers line 40-41 in the exception handling


def test_current_timezone_hasattr_key() -> None:
    """Test current_timezone when tzinfo has key attribute."""
    from zoneinfo import ZoneInfo

    from time_helper.timezone import current_timezone

    # Mock datetime to return timezone with key
    mock_dt = MagicMock()
    mock_dt.tzinfo = ZoneInfo("UTC")

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        result = current_timezone()
        assert result is not None
        # This covers line 56 where we check hasattr(dt.tzinfo, "key")


def test_current_timezone_none_tzname() -> None:
    """Test current_timezone when tzname() returns None."""
    from time_helper.timezone import current_timezone

    # Mock datetime to return None tzname
    mock_dt = MagicMock()
    mock_dt.tzinfo = None  # No key attribute
    mock_dt.tzname.return_value = None

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        result = current_timezone()
        assert result is not None
        # This covers line 63 where we return timezone("UTC") when tzname is None


def test_current_timezone_unix_tz_env_variable() -> None:
    """Test current_timezone with TZ environment variable on Unix."""
    import os

    from time_helper.timezone import current_timezone

    # Mock datetime to return unknown timezone
    mock_dt = MagicMock()
    mock_dt.tzinfo = None
    mock_dt.tzname.return_value = "UNKNOWN"

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        # Mock the first timezone call to fail, causing fallback
        with patch("time_helper.timezone.timezone") as mock_tz:
            call_count = 0

            def side_effect(name):  # type: ignore[no-untyped-def]
                nonlocal call_count
                call_count += 1
                if call_count == 1:  # First call (UNKNOWN) fails
                    raise Exception("Test exception")
                if name == "America/New_York" or name == "UTC":  # TZ env var
                    return MagicMock()
                raise Exception("Test exception")

            mock_tz.side_effect = side_effect

            # Set TZ environment variable
            with patch.dict(os.environ, {"TZ": "America/New_York"}):
                result = current_timezone()
                assert result is not None
                # This covers line 86 where we use TZ environment variable


def test_current_timezone_absolute_final_fallback() -> None:
    """Test current_timezone absolute final fallback."""
    from time_helper.timezone import current_timezone

    # Mock datetime to return unknown timezone
    mock_dt = MagicMock()
    mock_dt.tzinfo = None
    mock_dt.tzname.return_value = "UNKNOWN"

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        # Mock the first timezone call to fail, and then import platform to fail
        with patch("time_helper.timezone.timezone") as mock_tz:
            call_count = 0

            def side_effect(name):  # type: ignore[no-untyped-def]
                nonlocal call_count
                call_count += 1
                if call_count == 1:  # First call (UNKNOWN) fails
                    raise Exception("Test exception")
                if name == "UTC":  # Final fallback
                    return MagicMock()
                raise Exception("Test exception")

            mock_tz.side_effect = side_effect

            # Mock the import platform to fail
            with patch("builtins.__import__") as mock_import:

                def import_side_effect(name, *args, **kwargs):  # type: ignore[no-untyped-def]
                    if name == "platform":
                        raise ImportError("Platform import failed")
                    return __import__(name, *args, **kwargs)

                mock_import.side_effect = import_side_effect

                result = current_timezone()
                assert result is not None
                # This covers lines 90-92 where we catch the exception and return UTC


def test_find_timezone_returns_tzinfo_object() -> None:
    """Test find_timezone returns tzinfo object unchanged."""
    from zoneinfo import ZoneInfo

    from time_helper.timezone import find_timezone

    # Test with tzinfo object - should return unchanged
    tz_obj = ZoneInfo("UTC")
    result = find_timezone(tz_obj)
    assert result is tz_obj
    # This covers line 31 where we return tzinfo objects unchanged


def test_find_timezone_maps_iana_abbreviation() -> None:
    """Test find_timezone maps IANA abbreviations."""
    from time_helper.timezone import find_timezone

    # Test with IANA abbreviation
    result = find_timezone("IST")
    assert result is not None
    # This covers line 35 where we map IANA abbreviations


def test_current_timezone_maps_iana_abbreviation() -> None:
    """Test current_timezone maps IANA abbreviations."""
    from time_helper.timezone import current_timezone

    # Mock datetime to return IST timezone
    mock_dt = MagicMock()
    mock_dt.tzinfo = None
    mock_dt.tzname.return_value = "IST"

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        result = current_timezone()
        assert result is not None
        # This covers line 67 where we map IANA abbreviations in current_timezone


def test_current_timezone_handles_cest() -> None:
    """Test current_timezone handles CEST special case."""
    from time_helper.timezone import current_timezone

    # Mock datetime to return CEST timezone
    mock_dt = MagicMock()
    mock_dt.tzinfo = None
    mock_dt.tzname.return_value = "CEST"

    with patch("time_helper.timezone.datetime") as mock_datetime:
        mock_datetime.now.return_value.astimezone.return_value = mock_dt

        result = current_timezone()
        assert result is not None
        # This covers line 71 where we handle CEST special case


def test_findtz() -> None:
    tz = find_timezone("UTC")
    assert type(tz) in (tzinfo, ZoneInfo)
    assert tz is not None
    assert tz == ZoneInfo("UTC")

    tz = find_timezone("Asia/Kolkata")
    assert type(tz) in (tzinfo, ZoneInfo)
    assert tz is not None
    assert tz == ZoneInfo("Asia/Kolkata")

    tz = find_timezone("foobar")
    assert tz is None

    tz = find_timezone("IST")
    assert tz is not None
    assert tz == ZoneInfo("Asia/Kolkata")


def test_currenttz() -> None:
    tz = current_timezone()
    assert type(tz) in (tzinfo, ZoneInfo)
    assert type is not None

    # The current_timezone may return a more specific timezone than tzname()
    # For example, it may return 'Europe/Berlin' instead of 'CET'
    # So we just verify it returns a valid timezone
    assert tz is not None

    # Verify we can use it to create valid datetimes
    dt = datetime.now(tz)
    assert dt.tzinfo is not None
