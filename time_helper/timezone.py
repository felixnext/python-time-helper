"""Operations to handle different timezones."""

from __future__ import annotations

from datetime import datetime, tzinfo

try:
    from zoneinfo import ZoneInfo as timezone
except ImportError:
    # Python 3.10+ has zoneinfo built-in, no backports needed
    raise ImportError("zoneinfo not available")


IANA_MAPPING = {
    "IST": "Asia/Kolkata",  # Indian Standard Time (commonly intended)
    "EST": "America/New_York",  # Eastern Standard Time (US)
    "CST": "America/Chicago",  # Central Standard Time (US)
    "PST": "America/Los_Angeles",  # Pacific Standard Time (US)
    "BST": "Europe/London",  # British Summer Time
    "JST": "Asia/Tokyo",  # Japan Standard Time
    "CET": "Europe/Paris",  # Central European Time
    "EET": "Europe/Bucharest",  # Eastern European Time
    # Add more as needed, but always check for ambiguity!
}


def find_timezone(name: str | tzinfo | timezone) -> tzinfo | None:
    """Retrieves the given timezone by name."""
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
    """Retrieves the currently active timezone.

    Returns the system's current timezone as a proper tzinfo object.
    Handles abbreviations by mapping them to full IANA timezone names.
    """
    # Get the system's current timezone directly
    dt = datetime.now().astimezone()

    # If we already have a proper timezone object, return it
    if dt.tzinfo is not None and hasattr(dt.tzinfo, "key"):
        # This is already a proper ZoneInfo object
        return dt.tzinfo

    # Fall back to tzname and try to map it
    tzname = dt.tzname()

    if tzname is None:
        # If no timezone name, return UTC as fallback
        return timezone("UTC")

    # Check if it's an abbreviation that needs mapping
    if tzname in IANA_MAPPING:
        tzname = IANA_MAPPING[tzname]

    # Special case for CEST (not in our mapping)
    elif tzname == "CEST":
        tzname = "Europe/Berlin"  # More accurate than CET

    # Try to create timezone object
    try:
        return timezone(tzname)
    except Exception:
        # If all else fails, try to detect timezone using platform-specific methods
        try:
            import os
            import platform

            # On Unix-like systems, check TZ environment variable
            if platform.system() != "Windows":
                tz_env = os.environ.get("TZ")
                if tz_env:
                    return timezone(tz_env)

            # Last resort: return UTC
            return timezone("UTC")
        except Exception:
            # Final fallback
            return timezone("UTC")
