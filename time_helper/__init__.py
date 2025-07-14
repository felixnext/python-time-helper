# define the version
__version__ = "0.1.6"

import logging

try:
    from . import const as const
    from .convert import (
        any_to_datetime as any_to_datetime,
    )
    from .convert import (
        convert_to_datetime as convert_to_datetime,
    )
    from .convert import (
        localize_datetime as localize_datetime,
    )
    from .convert import (
        make_aware as make_aware,
    )
    from .convert import (
        make_unaware as make_unaware,
    )
    from .convert import (
        parse_time as parse_time,
    )
    from .convert import (
        unix_to_datetime as unix_to_datetime,
    )
    from .ops import has_timezone as has_timezone
    from .ops import round_time as round_time
    from .ops import time_diff as time_diff
    from .range import create_intervals as create_intervals
    from .range import time_to_interval as time_to_interval
    from .timezone import current_timezone as current_timezone
    from .timezone import find_timezone as find_timezone
    from .wrapper import DateTimeWrapper as DateTimeWrapper
except Exception:
    logging.error("Not all dependencies installed")

__all__ = [
    "DateTimeWrapper",
    "any_to_datetime",
    "const",
    "convert_to_datetime",
    "create_intervals",
    "current_timezone",
    "find_timezone",
    "has_timezone",
    "localize_datetime",
    "make_aware",
    "make_unaware",
    "parse_time",
    "round_time",
    "time_diff",
    "time_to_interval",
    "unix_to_datetime",
]
