"""Test Various Convert Functions"""

from datetime import datetime, timedelta

try:
    import zoneinfo
except ImportError:
    import backports.zoneinfo as zoneinfo

import pandas as pd
import pytest

from time_helper import has_timezone, localize_datetime, make_aware, make_unaware, parse_time, unix_to_datetime

LOCAL_TZ = datetime.now().astimezone().tzname()
LOCAL_TZ = "CET" if LOCAL_TZ == "CEST" else LOCAL_TZ


def test_parse():
    date_str = "2021-09-15"
    format = "%Y-%m-%d"
    orig_date = datetime(2021, 9, 15, tzinfo=zoneinfo.ZoneInfo("UTC"))

    # test the parsing
    dt = parse_time(date_str, format, "UTC")
    assert dt is not None
    assert dt == orig_date
    assert dt.tzinfo.tzname(None) == zoneinfo.ZoneInfo("UTC").tzname(None)

    date_str = "2021-09-15_20:14:50"
    format = "%Y-%m-%d_%H:%M:%S"
    orig_date = datetime(2021, 9, 15, 20, 14, 50, tzinfo=zoneinfo.ZoneInfo(LOCAL_TZ))

    # test the parsing
    dt = parse_time(date_str, format, LOCAL_TZ)
    assert dt is not None
    assert dt == orig_date
    assert dt.tzinfo.tzname(None) == zoneinfo.ZoneInfo(LOCAL_TZ).tzname(None)

    # test error case
    with pytest.raises(ValueError):
        parse_time("1020-13-32_12:34:21", format, "UTC")


def test_any():
    # TODO: implement
    pass


def test_unix():
    # pair to check
    unix = 1634394762
    date = datetime(2021, 10, 16, 14, 32, 42, tzinfo=zoneinfo.ZoneInfo("GMT"))

    # run conversion
    conv_date = unix_to_datetime(unix, "GMT")
    assert conv_date is not None
    assert conv_date.tzinfo is not None
    assert conv_date == date

    # test with string
    date_loc = localize_datetime(date, LOCAL_TZ)
    conv_date = unix_to_datetime(str(unix), LOCAL_TZ)
    assert conv_date is not None
    assert conv_date.tzinfo is not None
    assert conv_date == date_loc

    # test error case
    with pytest.raises(ValueError):
        unix_to_datetime("FOO", "UTC")


def test_localize():
    date = datetime(2020, 10, 15, 20, 15, 13)
    assert date.tzinfo is None

    # makes the date aware
    loc_date = localize_datetime(date)
    assert loc_date.tzinfo.tzname(None) == zoneinfo.ZoneInfo(LOCAL_TZ).tzname(None)
    assert date.date() == loc_date.date()
    assert date.time() == loc_date.time()

    # ensures that the aware date can be converted in timezone
    loc_date_2 = localize_datetime(loc_date, "Asia/Kolkata")
    assert loc_date_2.tzinfo.tzname(None) == zoneinfo.ZoneInfo("Asia/Kolkata").tzname(None)
    assert abs(date.date() - loc_date_2.date()) <= timedelta(days=1)
    assert date.time() != loc_date_2.time()

    # makes sure that conversion back restores original timezone
    loc_date_3 = localize_datetime(loc_date_2, LOCAL_TZ)
    assert loc_date_3.tzinfo.tzname(None) == zoneinfo.ZoneInfo(LOCAL_TZ).tzname(None)
    assert date.date() == loc_date_3.date()
    assert date.time() == loc_date_3.time()

    # make sure that timestamp gets changed
    loc_date_4 = localize_datetime(datetime(2021, 10, 21, 5, 44, 18), "UTC")
    loc_date_5 = localize_datetime(datetime(2021, 10, 21, 5, 44, 18), "Europe/Berlin")
    assert loc_date_4.timestamp() > loc_date_5.timestamp()
    assert loc_date_4.timestamp() == loc_date_5.timestamp() + (60 * 60 * 2)


def test_aware():
    # create basic date
    date = datetime(2020, 10, 15, 20, 15, 13)
    assert date.tzinfo is None

    # ensure that datetime gets added
    loc_date = make_aware(date, "Europe/Berlin")
    assert loc_date is not None
    assert loc_date.tzinfo is not None
    assert date.date() == loc_date.date()
    assert date.time() == loc_date.time()
    assert loc_date.tzinfo.tzname(None) == zoneinfo.ZoneInfo("Europe/Berlin").tzname(None)

    # check to make aware timezone aware
    loc_date = make_aware(loc_date, "Europe/Berlin")
    assert loc_date is not None
    assert loc_date.tzinfo is not None
    assert date.date() == loc_date.date()
    assert date.time() == loc_date.time()
    assert loc_date.tzinfo.tzname(None) == zoneinfo.ZoneInfo("Europe/Berlin").tzname(None)

    # check switch of timezone
    pre_date = localize_datetime(loc_date, "Asia/Calcutta")
    loc_date2 = make_aware(loc_date, "Asia/Calcutta")
    assert pre_date == loc_date2
    assert loc_date2 is not None
    assert loc_date2.tzinfo is not None
    assert date.date() == loc_date2.date()
    assert (date + timedelta(hours=3, minutes=30)).time() == loc_date2.time()
    assert loc_date2.tzinfo.tzname(None) == zoneinfo.ZoneInfo("Asia/Calcutta").tzname(None)

    # make none check
    loc_date = make_aware(None)
    assert loc_date is None

    # test pandas functions
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

    # check error cases
    val = make_aware(None, col=None)
    assert val is None
    with pytest.raises(AssertionError):
        make_aware(df, col=None)
    with pytest.raises(RuntimeError):
        make_aware(df, col="no_col")

    df_new = make_aware(df, col="date")
    assert has_timezone(df_new, "date") is True

    df = pd.DataFrame(
        [
            [
                "2020-06-06",
                "foo",
            ],
            ["2020-06-06", "bar"],
        ],
        columns=["date", "text"],
    )
    df_new = make_aware(df, col="date")
    assert has_timezone(df_new, "date") is True

    df_none = make_aware("")
    assert df_none is None

    # TODO: add additional test cases here


def test_unaware():
    # create data
    date1 = datetime(2021, 1, 1, 15, 10, 30)
    date1_utc = localize_datetime(date1, "UTC")
    date1_cet = localize_datetime(date1, "CET")

    assert date1_cet.timestamp() != date1_utc.timestamp()

    dt = make_unaware(date1)
    assert dt == date1

    dt = make_unaware(date1_utc)
    assert dt == date1

    dt = make_unaware(date1_cet)
    assert dt == date1 - timedelta(hours=1)

    dt = make_unaware(date1_cet, "UTC")
    assert dt == date1 - timedelta(hours=1)

    dt = make_unaware("2021-07-12")
    assert dt == datetime(2021, 7, 12)

    dt = make_unaware("")
    assert dt is None
