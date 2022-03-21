
from datetime import tzinfo

import pytest
try:
    import zoneinfo
except ImportError:
    import backports.zoneinfo as zoneinfo

from time_helper import find_timezone, current_timezone

LOCAL_TZ = "CET"


def test_findtz():
    tz = find_timezone("UTC")
    assert type(tz) in (tzinfo, zoneinfo.ZoneInfo)
    assert tz is not None
    assert tz == zoneinfo.ZoneInfo("UTC")

    tz = find_timezone("us/Eastern")
    assert type(tz) in (tzinfo, zoneinfo.ZoneInfo)
    assert tz is not None
    assert tz == zoneinfo.ZoneInfo("us/Eastern")

    tz = find_timezone("foobar")
    assert tz is None


def test_currenttz():
    tz = current_timezone()
    assert type(tz) in (tzinfo, zoneinfo.ZoneInfo)
    assert type is not None
    assert tz == zoneinfo.ZoneInfo(LOCAL_TZ)