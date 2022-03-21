'''
Wrapper Class for different time objects (including dates and datetimes).

This makes many of the functions first class citizens and can easily expose the datetime
'''

from datetime import datetime
from typing import Any


class DateTimeWrapper():
    def __init__(self, dt) -> None:
        self.dt = safe_datetime(dt)

    def __call__(self, *args: Any, **kwds: Any) -> datetime:
        if not args and not kwds:
            return self.dt
        # TODO: call action on the internal datetime object
