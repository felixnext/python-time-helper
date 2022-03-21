'''
Operations to handle different timezones.

'''

from typing import Union
from datetime import tzinfo, datetime

try:
    from zoneinfo import ZoneInfo as timezone
except ImportError:
    from backports.zoneinfo import ZoneInfo as timezone


def find_timezone(name: Union[str, tzinfo, timezone]) -> tzinfo:
    '''Retrieves the given timezone by name.'''
    # check if already converted
    if isinstance(name, (tzinfo, timezone)):
        return name

    # try to convert
    try:
        return timezone(name)
    except Exception:
        return None


def current_timezone() -> tzinfo:
    '''Retrieves the currently active timezone.'''
    return timezone(datetime.now().astimezone().tzname())
