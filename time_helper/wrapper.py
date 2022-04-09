'''
Wrapper Class for different time objects (including dates and datetimes).

This makes many of the functions first class citizens and can easily expose the datetime
'''

from datetime import datetime
from typing import Any

from time_helper.convert import any_to_datetime
from time_helper.ops import time_diff


class DateTimeWrapper():
    def __init__(self, dt) -> None:
        self.dt = any_to_datetime(dt)

    def __call__(self, *args: Any, **kwds: Any) -> datetime:
        if not args and not kwds:
            return self.dt
        # TODO: call action on the internal datetime object

    # TODO: overload operators
    def __sub__(self, other):
        # make sure to convert
        if not isinstance(other, DateTimeWrapper):
            other = DateTimeWrapper(other)

        # ensure to compute
        return time_diff(self.dt, other.dt)

