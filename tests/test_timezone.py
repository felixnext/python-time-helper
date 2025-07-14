from datetime import datetime, tzinfo

try:
    import zoneinfo
except ImportError:
    import backports.zoneinfo as zoneinfo

from time_helper import current_timezone, find_timezone

LOCAL_TZ = datetime.now().astimezone().tzname()
LOCAL_TZ = "CET" if LOCAL_TZ == "CEST" else LOCAL_TZ


def test_findtz():
    tz = find_timezone("UTC")
    assert type(tz) in (tzinfo, zoneinfo.ZoneInfo)
    assert tz is not None
    assert tz == zoneinfo.ZoneInfo("UTC")

    tz = find_timezone("Asia/Kolkata")
    assert type(tz) in (tzinfo, zoneinfo.ZoneInfo)
    assert tz is not None
    assert tz == zoneinfo.ZoneInfo("Asia/Kolkata")

    tz = find_timezone("foobar")
    assert tz is None

    tz = find_timezone("IST")
    assert tz is not None
    assert tz == zoneinfo.ZoneInfo("Asia/Kolkata")


def test_currenttz():
    tz = current_timezone()
    assert type(tz) in (tzinfo, zoneinfo.ZoneInfo)
    assert type is not None
    assert tz == zoneinfo.ZoneInfo(LOCAL_TZ)
