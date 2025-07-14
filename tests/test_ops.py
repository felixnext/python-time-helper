from datetime import datetime, timedelta

import pandas as pd
import pytest

from time_helper import has_timezone, localize_datetime, round_time, time_diff


def test_diff():
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
    diff1 = time_diff(date2, date1_utc, "UTC")
    assert diff1 == orig_diff
    diff2 = time_diff(date1_utc, date2, "UTC")
    assert diff2 == -orig_diff

    # localize further should not change inherit time
    date1_cal = localize_datetime(date1_utc, "Asia/Calcutta")
    diff1 = time_diff(date2, date1_utc, "UTC")
    assert diff1 == orig_diff

    # test different timezones (times are then compared in utc, so diff should remove 1 hour)
    date2_cet = localize_datetime(date2, "Europe/Berlin")
    diff1 = time_diff(date2_cet, date1_utc)
    assert diff1 == orig_diff - timedelta(hours=1)

    # convert the other timezone
    date1_cal = localize_datetime(date1, "Asia/Calcutta")
    diff1 = time_diff(date2_cet, date1_cal)
    assert diff1 == orig_diff + timedelta(hours=4, minutes=30)


def test_pandas_timezone():
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
        has_timezone(None, None)
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


def test_round_time():
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
