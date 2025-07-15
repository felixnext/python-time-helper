"""Natural language datetime parsing support."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any


def parse_natural(text: str, reference: datetime | None = None) -> datetime:
    """Parse natural language datetime expressions.

    Args:
        text: Natural language datetime expression
        reference: Reference datetime for relative expressions (default: now)

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If expression cannot be parsed

    Examples:
        >>> parse_natural("tomorrow")
        >>> parse_natural("next monday")
        >>> parse_natural("in 2 hours")
        >>> parse_natural("yesterday at 9am")
        >>> parse_natural("2 days ago")
    """
    if not text or not text.strip():
        raise ValueError("Empty expression")

    text = text.strip().lower()

    if reference is None:
        reference = datetime.now()

    # Handle timezone-aware reference
    if reference.tzinfo is not None:
        # Keep timezone info for result
        pass
    else:
        pass

    # Basic time references
    if text == "now":
        return reference

    if text == "today":
        return reference.replace(hour=0, minute=0, second=0, microsecond=0)

    if text == "tomorrow":
        return (reference + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    if text == "yesterday":
        return (reference - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Time of day references
    if text == "noon":
        return reference.replace(hour=12, minute=0, second=0, microsecond=0)

    if text == "midnight":
        return reference.replace(hour=0, minute=0, second=0, microsecond=0)

    # Morning/afternoon/evening/night
    if text == "morning":
        return reference.replace(hour=9, minute=0, second=0, microsecond=0)

    if text == "afternoon":
        return reference.replace(hour=14, minute=0, second=0, microsecond=0)

    if text == "evening":
        return reference.replace(hour=19, minute=0, second=0, microsecond=0)

    if text == "night":
        return reference.replace(hour=22, minute=0, second=0, microsecond=0)

    # Week/month/year references
    if text == "next week":
        return reference + timedelta(weeks=1)

    if text == "last week":
        return reference - timedelta(weeks=1)

    if text == "next month":
        if reference.month == 12:
            return reference.replace(year=reference.year + 1, month=1)
        return reference.replace(month=reference.month + 1)

    if text == "last month":
        if reference.month == 1:
            return reference.replace(year=reference.year - 1, month=12)
        return reference.replace(month=reference.month - 1)

    # Year references
    if text == "beginning of year":
        return reference.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    if text == "end of year":
        return reference.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

    # Month references
    if text == "beginning of month":
        return reference.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if text == "end of month":
        # Get last day of month
        next_month = reference.replace(day=28) + timedelta(days=4)
        last_day = (next_month - timedelta(days=next_month.day)).day
        return reference.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    # First/last day of month
    if text == "first of the month":
        return reference.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if text == "last day of the month":
        next_month = reference.replace(day=28) + timedelta(days=4)
        last_day = (next_month - timedelta(days=next_month.day)).day
        return reference.replace(day=last_day, hour=0, minute=0, second=0, microsecond=0)

    # Weekend references
    if text == "this weekend":
        days_until_saturday = (5 - reference.weekday()) % 7
        return reference + timedelta(days=days_until_saturday)

    if text == "next weekend":
        days_until_saturday = (5 - reference.weekday()) % 7
        if days_until_saturday == 0:  # Already Saturday
            days_until_saturday = 7
        return reference + timedelta(days=days_until_saturday + 7)

    if text == "last weekend":
        days_since_saturday = (reference.weekday() - 5) % 7
        if days_since_saturday == 0:  # Already Saturday
            days_since_saturday = 7
        return reference - timedelta(days=days_since_saturday)

    # Business day references
    if text == "next business day":
        next_day = reference + timedelta(days=1)
        while next_day.weekday() > 4:  # Skip weekends
            next_day += timedelta(days=1)
        return next_day

    if text == "last business day":
        prev_day = reference - timedelta(days=1)
        while prev_day.weekday() > 4:  # Skip weekends
            prev_day -= timedelta(days=1)
        return prev_day

    # Days of the week
    weekdays = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}

    for day_name, day_num in weekdays.items():
        if text == day_name:
            days_ahead = day_num - reference.weekday()
            if days_ahead < 0:  # Target day already happened this week
                days_ahead += 7
            return reference + timedelta(days=days_ahead)

        if text == f"next {day_name}":
            # For "next", we always want the next occurrence of this weekday
            days_ahead = day_num - reference.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return reference + timedelta(days=days_ahead)

        if text == f"last {day_name}":
            days_behind = reference.weekday() - day_num
            if days_behind <= 0:
                days_behind += 7
            return reference - timedelta(days=days_behind)

    # Handle timezone suffixes like "9am EST"
    tz_pattern = re.compile(r"^(.+)\s+(est|pst|cst|mst|utc|gmt)$")
    match = tz_pattern.match(text)
    if match:
        time_part = match.group(1).strip()
        _tz_part = match.group(2).strip().upper()

        # Parse the time part without timezone
        time_dt = parse_natural(time_part, reference)

        # For now, just return the time without timezone conversion
        # This could be enhanced to actually apply timezone conversion
        return time_dt

    # Time patterns (9am, 2:30pm, etc.)
    time_pattern = re.compile(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$")
    match = time_pattern.match(text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        ampm = match.group(3)

        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0

        return reference.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Relative time patterns (in X hours, X days ago, etc.)
    # "in X hours/minutes/days" or "X hours/minutes/days"
    in_pattern = re.compile(r"^(?:in )?(\d+) (hour|hours|minute|minutes|day|days|week|weeks)$")
    match = in_pattern.match(text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if unit.startswith("hour"):
            return reference + timedelta(hours=amount)
        if unit.startswith("minute"):
            return reference + timedelta(minutes=amount)
        if unit.startswith("day"):
            return reference + timedelta(days=amount)
        if unit.startswith("week"):
            return reference + timedelta(weeks=amount)

    # "X hours/minutes/days ago"
    ago_pattern = re.compile(r"^(\d+) (hour|hours|minute|minutes|day|days|week|weeks) ago$")
    match = ago_pattern.match(text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if unit.startswith("hour"):
            return reference - timedelta(hours=amount)
        if unit.startswith("minute"):
            return reference - timedelta(minutes=amount)
        if unit.startswith("day"):
            return reference - timedelta(days=amount)
        if unit.startswith("week"):
            return reference - timedelta(weeks=amount)

    # Complex expressions with "at" (tomorrow at 9am, monday at 2:30pm)
    at_pattern = re.compile(r"^(.+) at (.+)$")
    match = at_pattern.match(text)
    if match:
        day_part = match.group(1).strip()
        time_part = match.group(2).strip()

        # Parse the day part
        day_dt = parse_natural(day_part, reference)

        # Parse the time part
        time_dt = parse_natural(time_part, reference)

        # Combine them
        return day_dt.replace(
            hour=time_dt.hour, minute=time_dt.minute, second=time_dt.second, microsecond=time_dt.microsecond
        )

    # Ordinal patterns (15th of next month)
    ordinal_pattern = re.compile(r"^(\d+)(?:st|nd|rd|th) of (.+)$")
    match = ordinal_pattern.match(text)
    if match:
        day = int(match.group(1))
        month_part = match.group(2).strip()

        if month_part == "next month":
            if reference.month == 12:
                target_month = reference.replace(year=reference.year + 1, month=1)
            else:
                target_month = reference.replace(month=reference.month + 1)
            return target_month.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
        if month_part == "the month":
            return reference.replace(day=day, hour=0, minute=0, second=0, microsecond=0)

    # If we get here, we couldn't parse the expression
    raise ValueError(f"Cannot parse natural language expression: '{text}'")


def add_natural_language_support() -> None:
    """Add natural language parsing support to DateTimeWrapper."""
    from time_helper.wrapper import DateTimeWrapper

    # Store original __init__ to extend it
    original_init = DateTimeWrapper.__init__

    def enhanced_init(self: DateTimeWrapper, dt: Any, reference: datetime | None = None) -> None:
        """Enhanced __init__ with natural language support."""
        if isinstance(dt, str):
            # Try natural language parsing first
            try:
                parsed_dt = parse_natural(dt, reference)
                original_init(self, parsed_dt)
                return
            except ValueError:
                # Fall back to regular parsing
                pass

        # Use original initialization
        original_init(self, dt)

    # Add method to add natural language offsets
    def add_natural(self: DateTimeWrapper, text: str) -> DateTimeWrapper:
        """Add a natural language time offset to the datetime."""
        if self.dt is None:
            raise ValueError("Cannot add to None datetime")

        # For simple duration expressions like "1 day", treat as relative
        if re.match(r"^\d+ (hour|hours|minute|minutes|day|days|week|weeks)$", text):
            # Parse as "in X units" to get relative offset
            offset_dt = parse_natural(f"in {text}", self.dt)
            return DateTimeWrapper(offset_dt)

        # Parse the offset using current datetime as reference
        offset_dt = parse_natural(text, self.dt)

        # Calculate the difference
        diff = offset_dt - self.dt

        # Add the difference to current datetime
        new_dt = self.dt + diff

        return DateTimeWrapper(new_dt)

    # Monkey patch the methods
    DateTimeWrapper.__init__ = enhanced_init  # type: ignore[method-assign]
    DateTimeWrapper.add_natural = add_natural  # type: ignore[attr-defined]


# Initialize natural language support
add_natural_language_support()
