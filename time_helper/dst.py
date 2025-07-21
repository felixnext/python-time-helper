"""DST (Daylight Saving Time) support functions."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TypedDict
from zoneinfo import ZoneInfo

from .timezone import find_timezone


class DSTTransition(TypedDict):
    """Type for DST transition information."""

    type: str  # "spring_forward" or "fall_back"
    date: datetime


def is_dst_active(dt: datetime | None) -> bool:
    """Check if DST is currently active for the given datetime.

    Args:
        dt: Timezone-aware datetime to check

    Returns:
        True if DST is active, False otherwise

    Raises:
        ValueError: If datetime is None or not timezone-aware
    """
    if dt is None:
        raise ValueError("Cannot check DST for None datetime")

    if dt.tzinfo is None:
        raise ValueError("Cannot check DST for timezone-unaware datetime")

    # Get DST offset
    dst_offset = dt.dst()

    # DST is active if offset is greater than zero
    return dst_offset is not None and dst_offset > timedelta(0)


def get_dst_transitions(timezone: str | ZoneInfo, year: int) -> list[DSTTransition]:
    """Get DST transition dates for a timezone in a given year.

    Args:
        timezone: Timezone name or ZoneInfo object
        year: Year to get transitions for

    Returns:
        List of DST transitions with type and date
    """
    # Convert timezone string to ZoneInfo if needed
    if isinstance(timezone, str):
        tz_obj = find_timezone(timezone)
        if tz_obj is None:
            raise ValueError(f"Invalid timezone: {timezone}")
        tz = tz_obj
    else:
        tz = timezone

    transitions = []

    # Check each day of the year for DST changes
    prev_dst = None
    for month in range(1, 13):
        # Get days in month
        if month == 2:
            days = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
        elif month in [4, 6, 9, 11]:
            days = 30
        else:
            days = 31

        for day in range(1, days + 1):
            try:
                # Check at 12:00 to avoid ambiguous times
                dt = datetime(year, month, day, 12, 0, tzinfo=tz)
                current_dst = dt.dst()

                if prev_dst is not None and current_dst != prev_dst:
                    # DST transition detected
                    trans_type = (
                        "spring_forward" if (current_dst or timedelta(0)) > (prev_dst or timedelta(0)) else "fall_back"
                    )

                    # Find exact transition time by checking hourly
                    for hour in range(24):
                        try:
                            check_dt = datetime(year, month, day, hour, 0, tzinfo=tz)
                            if check_dt.dst() != prev_dst:
                                transitions.append(DSTTransition(type=trans_type, date=check_dt))
                                break
                        except Exception:
                            # Might hit non-existent time
                            if trans_type == "spring_forward":
                                transitions.append(
                                    DSTTransition(type=trans_type, date=datetime(year, month, day, hour, 0, tzinfo=tz))
                                )
                                break

                prev_dst = current_dst

            except Exception:
                # Handle invalid dates
                continue

    return transitions


def next_dst_transition(dt: datetime) -> DSTTransition | None:
    """Find the next DST transition from the given datetime.

    Args:
        dt: Timezone-aware datetime to start from

    Returns:
        Next DST transition info or None if no transition found

    Raises:
        ValueError: If datetime is None or not timezone-aware
    """
    if dt is None:
        raise ValueError("Cannot find DST transition for None datetime")

    if dt.tzinfo is None:
        raise ValueError("Cannot find DST transition for timezone-unaware datetime")

    # Get transitions for current year
    if not isinstance(dt.tzinfo, ZoneInfo):
        raise ValueError("DST transitions only supported for ZoneInfo timezones")
    transitions = get_dst_transitions(dt.tzinfo, dt.year)

    # Find next transition after current datetime
    for trans in transitions:
        if trans["date"] > dt:
            return trans

    # Check next year if no transition found in current year
    next_year_transitions = get_dst_transitions(dt.tzinfo, dt.year + 1)
    if next_year_transitions:
        return next_year_transitions[0]

    return None
