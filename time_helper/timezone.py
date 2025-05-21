'''
Operations to handle different timezones.

'''

from typing import Union
from datetime import tzinfo, datetime

try:
    from zoneinfo import ZoneInfo as timezone
except ImportError:
    from backports.zoneinfo import ZoneInfo as timezone


IANA_MAPPING = {
    "IST": "Asia/Kolkata",       # Indian Standard Time (commonly intended)
    "EST": "America/New_York",   # Eastern Standard Time (US)
    "CST": "America/Chicago",    # Central Standard Time (US)
    "PST": "America/Los_Angeles",# Pacific Standard Time (US)
    "BST": "Europe/London",      # British Summer Time
    "JST": "Asia/Tokyo",         # Japan Standard Time
    "CET": "Europe/Paris",       # Central European Time
    "EET": "Europe/Bucharest",   # Eastern European Time
    # Add more as needed, but always check for ambiguity!
}


def find_timezone(name: Union[str, tzinfo, timezone]) -> tzinfo:
    '''Retrieves the given timezone by name.'''
    # check if already converted
    if isinstance(name, (tzinfo, timezone)):
        return name
    
    # note: IANA tz are not covered by `ZoneInfo` so need to map
    if isinstance(name, str) and name in IANA_MAPPING:
        name = IANA_MAPPING[name]

    # try to convert
    try:
        return timezone(name)
    except Exception:
        return None


def current_timezone() -> tzinfo:
    '''Retrieves the currently active timezone.'''
    # retrieve the current timezone name
    cur = datetime.now().astimezone().tzname()

    # special cases
    # note: this timezone is not available through the data (summer-time)
    if cur == "CEST":
        cur = "CET"

    return timezone(cur)
