"""Simple tests to maintain coverage for convert.py."""

import sys
from datetime import date, datetime, time
from unittest.mock import MagicMock, patch

import pytest

from time_helper import localize_datetime, make_aware, make_unaware, unix_to_datetime
from time_helper.convert import any_to_datetime, convert_to_datetime


class TestConvertCoverage:
    """Simple tests for convert.py coverage."""

    def test_zoneinfo_import_error(self) -> None:
        """Test ImportError when zoneinfo is not available."""
        with patch.dict(sys.modules, {"zoneinfo": None}), pytest.raises(ImportError, match="zoneinfo not available"):
            import importlib

            import time_helper.convert

            importlib.reload(time_helper.convert)

    def test_unix_to_datetime_with_failed_localization(self) -> None:
        """Test unix_to_datetime when localization fails."""
        with (
            patch("time_helper.convert.localize_datetime", return_value=None),
            pytest.raises(ValueError, match="Failed to localize datetime"),
        ):
            unix_to_datetime(1234567890, tz="America/New_York")

    def test_any_to_datetime_with_logger(self) -> None:
        """Test any_to_datetime with logger."""
        mock_logger = MagicMock()

        # Use a date string with custom format to ensure it goes through the format loop
        result = any_to_datetime("15/01/2024", logger=mock_logger, date_format="%d/%m/%Y")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        # Logger should have been called
        assert mock_logger.info.called

    def test_any_to_datetime_with_date_object(self) -> None:
        """Test any_to_datetime with date object."""
        test_date = date(2024, 7, 15)
        result = any_to_datetime(test_date)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 7
        assert result.day == 15
        assert result.hour == 0
        assert result.minute == 0

    def test_convert_to_datetime_with_time_object(self) -> None:
        """Test convert_to_datetime with time object."""
        test_time = time(14, 30, 45)
        baseline = datetime(2024, 1, 15, 12, 0, 0)

        result = convert_to_datetime(test_time, baseline=baseline)
        assert isinstance(result, datetime)
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45

    def test_convert_to_datetime_with_date_object(self) -> None:
        """Test convert_to_datetime with date object."""
        test_date = date(2024, 1, 15)

        result = convert_to_datetime(test_date)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.hour == 12  # Default noon

    def test_convert_to_datetime_with_invalid_type(self) -> None:
        """Test convert_to_datetime with invalid type."""
        with pytest.raises(ValueError, match="Given datetime data has unkown type"):
            convert_to_datetime("not a datetime")  # type: ignore[arg-type]

    def test_localize_datetime_with_none(self) -> None:
        """Test localize_datetime with None datetime."""
        result = localize_datetime(None, "UTC")
        assert result is None

    def test_localize_datetime_with_invalid_timezone(self) -> None:
        """Test localize_datetime with invalid string timezone."""
        dt = datetime(2024, 1, 15, 12, 0, 0)

        with (
            patch("time_helper.convert.find_timezone", return_value=None),
            pytest.raises(ValueError, match="Invalid timezone"),
        ):
            localize_datetime(dt, "Invalid/Timezone")

    def test_make_aware_with_none(self) -> None:
        """Test make_aware with None datetime."""
        result = make_aware(None, tz="UTC")
        assert result is None

    def test_make_aware_already_aware(self) -> None:
        """Test make_aware with already aware datetime."""
        from zoneinfo import ZoneInfo

        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        result = make_aware(dt)
        assert result == dt
        assert result.tzinfo is not None

    def test_make_aware_with_current_timezone(self) -> None:
        """Test make_aware with None tz."""
        dt = datetime(2024, 1, 15, 12, 0, 0)

        with patch("time_helper.convert.current_timezone") as mock_current_tz:
            from zoneinfo import ZoneInfo

            mock_current_tz.return_value = ZoneInfo("America/New_York")

            result = make_aware(dt)
            assert result is not None
            assert result.tzinfo is not None

    def test_make_unaware_with_failed_localization(self) -> None:
        """Test make_unaware when localization fails."""
        dt = datetime(2024, 1, 15, 12, 0, 0)

        with patch("time_helper.convert.localize_datetime", return_value=None):
            result = make_unaware(dt, tz="America/New_York")
            assert result is None
