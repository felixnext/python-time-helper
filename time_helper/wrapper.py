'''
Wrapper Class for different time objects (including dates and datetimes).

This makes many of the functions first class citizens and can easily expose the datetime
'''

from datetime import datetime
from typing import Any, Union
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from time_helper.convert import any_to_datetime, localize_datetime
from time_helper.ops import time_diff


class DateTimeWrapper():
    def __init__(self, dt: Union[datetime, str, Any], timezone: Union[str, ZoneInfo] = None) -> None:
        # retrieve the datetime
        self.dt = any_to_datetime(dt)

        # check if a timezone is set
        if timezone:
            self.dt = localize_datetime(self.dt, timezone)

    def __call__(self, *args: Any, **kwds: Any) -> datetime:
        if not args and not kwds:
            return self.dt

        # TODO: add code that allows to localize?

    def __getattribute__(self, __name: str) -> Any:
        if hasattr(self.dt, __name):
            return getattr(self.dt, __name)
        return None

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, DateTimeWrapper):
            return self.dt == __o.dt
        return self.dt == __o


    # TODO: overload operators
    def __sub__(self, other):
        # make sure to convert
        if not isinstance(other, DateTimeWrapper):
            other = DateTimeWrapper(other)

        # ensure to compute
        return time_diff(self.dt, other.dt)

