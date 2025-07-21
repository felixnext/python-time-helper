"""Wrapper Class for different time objects (including dates and datetimes).

This makes many of the functions first class citizens and can easily expose the datetime
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from .convert import any_to_datetime, localize_datetime, make_aware, make_unaware
from .ops import round_time, time_diff

if TYPE_CHECKING:
    from datetime import tzinfo


class DateTimeWrapper:
    """Wrapper class for datetime objects with additional operations.

    This wrapper provides a fluent interface for datetime operations,
    allowing method chaining and easier manipulation of datetime objects.
    """

    def __init__(self, dt: Any) -> None:
        """Initialize wrapper with datetime-like object.

        Args:
            dt: Any datetime-like object (string, datetime, date, timestamp, or another wrapper)
        """
        if isinstance(dt, DateTimeWrapper):
            self.dt: datetime | None = dt.dt
        else:
            self.dt = any_to_datetime(dt)

    def __call__(self, *args: Any, **kwds: Any) -> datetime | None:
        """Return the wrapped datetime object."""
        if not args and not kwds:
            return self.dt
        return self.dt

    # Arithmetic operators
    def __add__(self, other: timedelta) -> DateTimeWrapper:
        """Add timedelta to wrapped datetime."""
        if not isinstance(other, timedelta):
            return NotImplemented
        if self.dt is None:
            return DateTimeWrapper(None)
        return DateTimeWrapper(self.dt + other)

    def __sub__(self, other: Any) -> timedelta | DateTimeWrapper:
        """Subtract datetime or timedelta from wrapped datetime."""
        if isinstance(other, timedelta):
            if self.dt is None:
                return DateTimeWrapper(None)
            return DateTimeWrapper(self.dt - other)

        # Convert to wrapper if needed
        if not isinstance(other, DateTimeWrapper):
            other = DateTimeWrapper(other)

        # Compute time difference
        if self.dt is None or other.dt is None:
            raise ValueError("Cannot compute time diff with None datetime")
        return time_diff(self.dt, other.dt)

    # Comparison operators
    def __eq__(self, other: Any) -> bool:
        """Check equality with another datetime-like object."""
        if not isinstance(other, DateTimeWrapper):
            other = DateTimeWrapper(other)
        return bool(self.dt == other.dt)

    def __ne__(self, other: Any) -> bool:
        """Check inequality with another datetime-like object."""
        return not self.__eq__(other)

    def __lt__(self, other: Any) -> bool:
        """Check if less than another datetime-like object."""
        if not isinstance(other, DateTimeWrapper):
            other = DateTimeWrapper(other)
        if self.dt is None or other.dt is None:
            return False
        return bool(self.dt < other.dt)

    def __le__(self, other: Any) -> bool:
        """Check if less than or equal to another datetime-like object."""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: Any) -> bool:
        """Check if greater than another datetime-like object."""
        if not isinstance(other, DateTimeWrapper):
            other = DateTimeWrapper(other)
        if self.dt is None or other.dt is None:
            return False
        return bool(self.dt > other.dt)

    def __ge__(self, other: Any) -> bool:
        """Check if greater than or equal to another datetime-like object."""
        return self.__gt__(other) or self.__eq__(other)

    # String representations
    def __str__(self) -> str:
        """Return ISO format string representation."""
        if self.dt is None:
            return "None"
        return self.dt.isoformat()

    def __repr__(self) -> str:
        """Return detailed string representation."""
        if self.dt is None:
            return "DateTimeWrapper(None)"
        return f"DateTimeWrapper({self.dt.isoformat()})"

    # Timezone operations
    def make_aware(self, tz: str | tzinfo | None = None) -> DateTimeWrapper:
        """Make datetime timezone-aware.

        Args:
            tz: Timezone name or tzinfo object

        Returns:
            New DateTimeWrapper with timezone-aware datetime
        """
        if self.dt is None:
            return DateTimeWrapper(None)
        aware_dt = make_aware(self.dt, tz)
        return DateTimeWrapper(aware_dt)

    def make_unaware(self, tz: str | tzinfo | None = None) -> DateTimeWrapper:
        """Remove timezone information.

        Args:
            tz: Optional timezone to convert to before removing tzinfo

        Returns:
            New DateTimeWrapper with timezone-unaware datetime
        """
        if self.dt is None:
            return DateTimeWrapper(None)
        unaware_dt = make_unaware(self.dt, tz)  # type: ignore[arg-type]
        return DateTimeWrapper(unaware_dt)

    def localize(self, tz: str | tzinfo) -> DateTimeWrapper:
        """Convert datetime to different timezone.

        Args:
            tz: Target timezone name or tzinfo object

        Returns:
            New DateTimeWrapper with datetime in target timezone
        """
        if self.dt is None:
            return DateTimeWrapper(None)
        localized_dt = localize_datetime(self.dt, tz)
        return DateTimeWrapper(localized_dt)

    # Time operations
    def round(self, freq: str = "D", max_out: bool = False) -> DateTimeWrapper:
        """Round datetime to specified frequency.

        Args:
            freq: Frequency to round to (S, M, H, D, W, m, Y)
            max_out: If True, round to end of period instead of start

        Returns:
            New DateTimeWrapper with rounded datetime
        """
        if self.dt is None:
            return DateTimeWrapper(None)
        rounded_dt = round_time(self.dt, freq, max_out)
        return DateTimeWrapper(rounded_dt)

    # Conversion methods
    def to_string(self, format: str | None = None) -> str:
        """Convert to string with optional format.

        Args:
            format: strftime format string (defaults to ISO format)

        Returns:
            Formatted datetime string
        """
        if self.dt is None:
            return "None"
        if format is None:
            return self.dt.isoformat()
        return self.dt.strftime(format)

    def to_timestamp(self) -> float:
        """Convert to unix timestamp.

        Returns:
            Unix timestamp as float
        """
        if self.dt is None:
            raise ValueError("Cannot convert None to timestamp")
        return self.dt.timestamp()

    # Properties for easy access to datetime attributes
    @property
    def year(self) -> int:
        """Get year."""
        if self.dt is None:
            raise AttributeError("Cannot access year of None datetime")
        return self.dt.year

    @property
    def month(self) -> int:
        """Get month."""
        if self.dt is None:
            raise AttributeError("Cannot access month of None datetime")
        return self.dt.month

    @property
    def day(self) -> int:
        """Get day."""
        if self.dt is None:
            raise AttributeError("Cannot access day of None datetime")
        return self.dt.day

    @property
    def hour(self) -> int:
        """Get hour."""
        if self.dt is None:
            raise AttributeError("Cannot access hour of None datetime")
        return self.dt.hour

    @property
    def minute(self) -> int:
        """Get minute."""
        if self.dt is None:
            raise AttributeError("Cannot access minute of None datetime")
        return self.dt.minute

    @property
    def second(self) -> int:
        """Get second."""
        if self.dt is None:
            raise AttributeError("Cannot access second of None datetime")
        return self.dt.second

    @property
    def weekday(self) -> int:
        """Get day of week (0=Monday, 6=Sunday)."""
        if self.dt is None:
            raise AttributeError("Cannot access weekday of None datetime")
        return self.dt.weekday()

    @property
    def timezone(self) -> tzinfo | None:
        """Get timezone info."""
        if self.dt is None:
            raise AttributeError("Cannot access timezone of None datetime")
        return self.dt.tzinfo
