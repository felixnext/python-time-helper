"""Wrapper Class for different time objects (including dates and datetimes).

This makes many of the functions first class citizens and can easily expose the datetime
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from time_helper.convert import any_to_datetime
from time_helper.ops import time_diff


class DateTimeWrapper:
    """Wrapper class for datetime objects with additional operations."""

    def __init__(self, dt: Any) -> None:
        self.dt = any_to_datetime(dt)

    def __call__(self, *args: Any, **kwds: Any) -> datetime | None:
        """Return the wrapped datetime object."""
        if not args and not kwds:
            return self.dt
        # TODO: call action on the internal datetime object
        return self.dt

    # TODO: overload operators
    def __sub__(self, other: Any) -> timedelta:
        # make sure to convert
        if not isinstance(other, DateTimeWrapper):
            other = DateTimeWrapper(other)

        # ensure to compute
        if self.dt is None or other.dt is None:
            raise ValueError("Cannot compute time diff with None datetime")
        return time_diff(self.dt, other.dt)
