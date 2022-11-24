# define the version
__version__ = "0.1.5"

import logging

try:
    from . import const
    from .timezone import find_timezone, current_timezone

    from .convert import (
        parse_time,
        unix_to_datetime,
        any_to_datetime,
        convert_to_datetime,
        localize_datetime,
        make_aware,
        make_unaware,
    )

    from .ops import has_timezone, time_diff, round_time

    from .range import time_to_interval, create_intervals

    from .wrapper import DateTimeWrapper
except Exception:
    logging.error("Not all dependencies installed")
