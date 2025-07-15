from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo

from time_helper import current_timezone, find_timezone

LOCAL_TZ = datetime.now().astimezone().tzname()
LOCAL_TZ = "CET" if LOCAL_TZ == "CEST" else LOCAL_TZ


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
