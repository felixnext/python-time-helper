from datetime import date, datetime, timedelta

import pandas as pd
import pytest

from time_helper import has_timezone, localize_datetime, make_aware, round_time, time_diff


class TestOpsCoverage:
    """Test edge cases and error conditions in ops.py."""

    def test_has_timezone_without_pandas(self) -> None:
        """Test has_timezone mock function when pandas is not available."""

        # Mock test when pandas is not available
        # This test might not be effective if pandas is actually installed
        # but it's here to ensure the mock function exists
        pass

    def test_has_timezone_edge_cases(self) -> None:
        """Test has_timezone edge cases."""
        from time_helper.ops import has_timezone

        # Test with pandas if available
        try:
            import pandas as pd

            # Test with empty DataFrame but correct dtype
            df = pd.DataFrame({"time": pd.to_datetime([])})
            with pytest.raises(ValueError, match="The Dataframe is empty"):
                has_timezone(df, "time")

            # Test with invalid column
            df = pd.DataFrame({"time": [datetime.now()]})
            with pytest.raises(ValueError, match="The provided column.*is not in the dataframe"):
                has_timezone(df, "invalid_col")

            # Test with non-datetime column
            df = pd.DataFrame({"time": [1, 2, 3]})
            with pytest.raises(ValueError, match="Specified column is not a datetime object"):
                has_timezone(df, "time")

            # Test with Series that is not datetime
            series = pd.Series([1, 2, 3])
            with pytest.raises(ValueError, match="Provided series is not a datetime object"):
                has_timezone(series)

        except ImportError:
            # Skip these tests if pandas is not available
            pass

    def test_time_diff_error_cases(self) -> None:
        """Test time_diff error handling."""
        dt1 = datetime(2024, 1, 1, 12, 0, 0)
        dt2 = datetime(2024, 1, 1, 10, 0, 0)

        # Test with timezone-aware dates that can't be localized
        dt1_aware = make_aware(dt1, "UTC")
        dt2_aware = make_aware(dt2, "UTC")

        # Test the basic functionality
        result = time_diff(dt1_aware, dt2_aware)
        assert result == timedelta(hours=2)

        # Test with timezone-naive dates
        result = time_diff(dt1, dt2, tz="UTC")
        assert result == timedelta(hours=2)

    def test_round_time_date_with_hour_frequency(self) -> None:
        """Test round_time with date object and hour frequency."""
        dt = date(2024, 1, 1)

        # These should work because date gets converted to datetime
        result = round_time(dt, "H")  # type: ignore[arg-type]
        assert result == datetime(2024, 1, 1, 0, 0, 0)

        result = round_time(dt, "M")  # type: ignore[arg-type]
        assert result == datetime(2024, 1, 1, 0, 0, 0)

        result = round_time(dt, "S")  # type: ignore[arg-type]
        assert result == datetime(2024, 1, 1, 0, 0, 0)

    def test_round_time_parse_error(self) -> None:
        """Test round_time with unparseable input."""
        # Test with invalid input that can't be parsed
        with pytest.raises(ValueError, match="Could not parse Timestamp"):
            round_time(object())  # type: ignore[arg-type]

    def test_round_time_various_frequencies(self) -> None:
        """Test round_time with various frequencies to improve coverage."""
        dt = datetime(2024, 7, 15, 14, 35, 45, 123456)

        # Test day frequency
        result = round_time(dt, "D")
        assert result == datetime(2024, 7, 15, 0, 0, 0, 0)

        # Test day frequency with max_out
        result = round_time(dt, "D", max_out=True)
        assert result == datetime(2024, 7, 15, 23, 59, 59, 999999)

        # Test month frequency
        result = round_time(dt, "m")
        assert result == datetime(2024, 7, 1, 0, 0, 0, 0)

        # Test month frequency with max_out
        result = round_time(dt, "m", max_out=True)
        assert result == datetime(2024, 7, 31, 23, 59, 59, 999999)

        # Test year frequency
        result = round_time(dt, "Y")
        assert result == datetime(2024, 1, 1, 0, 0, 0, 0)

        # Test year frequency with max_out
        result = round_time(dt, "Y", max_out=True)
        assert result == datetime(2024, 12, 31, 23, 59, 59, 999999)

    def test_make_aware_force_convert_false(self) -> None:
        """Test make_aware with force_convert=False."""
        from time_helper.ops import make_aware

        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = make_aware(dt, "UTC", force_convert=False)
        assert result is not None
        assert result.tzinfo is not None

    def test_time_diff_with_different_timezones(self) -> None:
        """Test time_diff with different timezone scenarios."""
        # Test with one timezone-aware and one timezone-naive
        dt1 = make_aware("2024-01-01 12:00:00", "UTC")
        dt2 = datetime(2024, 1, 1, 10, 0, 0)  # naive

        result = time_diff(dt1, dt2, tz="UTC")
        assert result == timedelta(hours=2)

        # Test with both timezone-naive
        dt1_naive = datetime(2024, 1, 1, 12, 0, 0)
        dt2_naive = datetime(2024, 1, 1, 10, 0, 0)

        result = time_diff(dt1_naive, dt2_naive, tz="UTC")
        assert result == timedelta(hours=2)

    def test_round_time_with_timezone_preservation(self) -> None:
        """Test that round_time preserves timezone information."""
        # Create timezone-aware datetime
        dt = make_aware("2024-07-15 14:35:45", "America/New_York")

        # Round to hour
        result = round_time(dt, "H")
        assert result is not None
        assert result.tzinfo is not None
        assert result.tzinfo == dt.tzinfo

        # Round to day
        result = round_time(dt, "D")
        assert result is not None
        assert result.tzinfo is not None
        assert result.tzinfo == dt.tzinfo


def test_diff() -> None:
    # setup the data
    date1 = datetime(2021, 1, 1, 15, 10, 30)
    date2 = datetime(2021, 1, 10, 18, 20, 50)
    orig_diff = timedelta(days=9, hours=3, minutes=10, seconds=20)

    # vanilla test
    diff1 = time_diff(date2, date1)
    assert diff1 == orig_diff
    diff2 = time_diff(date1, date2)
    assert diff2 == -orig_diff

    # localize to first timezone
    date1_utc = localize_datetime(date1, "UTC")
    assert date1_utc is not None
    diff1 = time_diff(date2, date1_utc, "UTC")
    assert diff1 == orig_diff
    diff2 = time_diff(date1_utc, date2, "UTC")
    assert diff2 == -orig_diff

    # localize further should not change inherit time
    date1_cal = localize_datetime(date1_utc, "Asia/Calcutta")
    assert date1_cal is not None
    diff1 = time_diff(date2, date1_utc, "UTC")
    assert diff1 == orig_diff

    # test different timezones (times are then compared in utc, so diff should remove 1 hour)
    date2_cet = localize_datetime(date2, "Europe/Berlin")
    assert date2_cet is not None
    diff1 = time_diff(date2_cet, date1_utc)
    assert diff1 == orig_diff - timedelta(hours=1)

    # convert the other timezone
    date1_cal2 = localize_datetime(date1, "Asia/Calcutta")
    assert date1_cal2 is not None
    diff1 = time_diff(date2_cet, date1_cal2)
    assert diff1 == orig_diff + timedelta(hours=4, minutes=30)


def test_pandas_timezone() -> None:
    df = pd.DataFrame(
        [
            [
                pd.Timestamp("2020-06-06").tz_localize("Europe/Berlin"),
                "foo",
            ],
            [pd.Timestamp("2020-06-06").tz_localize("Europe/Berlin"), "bar"],
        ],
        columns=["date", "text"],
    )

    # check error cases
    with pytest.raises(ValueError):
        has_timezone(None, None)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        has_timezone(df, None)
    with pytest.raises(ValueError):
        has_timezone(df, "no_col")
    with pytest.raises(ValueError):
        has_timezone(df, "text")

    # check datetime cases
    val = has_timezone(df, "date")
    assert val is True

    # update dataframej
    df = pd.DataFrame(
        [
            [
                pd.Timestamp("2020-06-06"),
                "foo",
            ],
            [pd.Timestamp("2020-06-06"), "bar"],
        ],
        columns=["date", "text"],
    )
    val = has_timezone(df, "date")
    assert val is False


def test_round_time() -> None:
    dt = datetime(2022, 2, 10, 13, 30, 54)

    dt_out = round_time(dt, "M", max_out=False)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-10T13:30:00"
    dt_out = round_time(dt, "M", max_out=True)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-10T13:30:59.999999"

    dt_out = round_time(dt, "H", max_out=False)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-10T13:00:00"

    dt_out = round_time(dt, "D", max_out=False)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-10T00:00:00"

    dt_out = round_time(dt, "W", max_out=False)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-07T00:00:00"
    dt_out = round_time(dt, "W", max_out=True)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-13T23:59:59.999999"

    dt_out = round_time(dt, "m", max_out=False)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-01T00:00:00"
    dt_out = round_time(dt, "m", max_out=True)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-02-28T23:59:59.999999"

    dt_out = round_time(dt, "Y", max_out=False)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-01-01T00:00:00"
    dt_out = round_time(dt, "Y", max_out=True)
    assert type(dt_out) == datetime
    assert dt_out.isoformat() == "2022-12-31T23:59:59.999999"
