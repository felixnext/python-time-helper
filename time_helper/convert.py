"""All conversion function. This includes conversions between different datetimes."""

from __future__ import annotations

from datetime import date, datetime, time, tzinfo
from logging import Logger
from typing import Any

from dateutil import parser

# try to import various dependend libraries
try:
    from zoneinfo import ZoneInfo as timezone
except ImportError:
    # Python 3.10+ has zoneinfo built-in, no backports needed
    raise ImportError("zoneinfo not available")
try:
    import pandas as pd
    from pandas import DataFrame, Series, to_datetime
    from pandas.api.types import is_datetime64_any_dtype as is_datetime
except Exception:
    pd = None  # type: ignore[assignment]
    Series = None  # type: ignore[assignment,misc]
    DataFrame = None  # type: ignore[assignment,misc]

    def is_datetime(x: Any) -> bool:  # type: ignore[misc] # noqa: ARG001
        """Mock function when pandas is not installed."""
        return False

    def to_datetime(x: Any, **kwargs: Any) -> None:  # type: ignore[no-redef] # noqa: ARG001
        """Mock function when pandas is not installed."""
        return None  # noqa: RET501


try:
    import numpy as np
    from numpy import array as nparray
except Exception:
    np = None  # type: ignore[assignment]
    nparray = None  # type: ignore[assignment]
import contextlib

from pytz import AmbiguousTimeError

from time_helper.const import DATE_FORMATS
from time_helper.timezone import current_timezone, find_timezone


def parse_time(time_str: str, format: str, timezone: tzinfo | timezone | str) -> datetime:
    """Parses the given time based on the format and timezone (if provdied).

    Args:
        time_str: String value that should be parsed
        format: Format to parse the time from
        timezone: Timezone that should be applied (either str or actual timezone)

    Returns:
        (timzone-aware) datetime object
    """
    # check the current timezone
    tz = find_timezone(timezone)

    # update
    dt = time_str if isinstance(time_str, datetime) else datetime.strptime(time_str, format)
    if tz is not None:
        dt = dt.replace(tzinfo=tz)
    return dt


def unix_to_datetime(ts: str | int | float | Any, tz: timezone | str | Any = None) -> datetime:
    """Converts the given objects into a datetime.

    Args:
        ts: `int` or `long` that contains the timestamp
        tz: `pytz.timezone` that is used for localization

    Returns:
        `datetime` object that contains the time
    """
    # check if should be parsed
    if isinstance(ts, str):
        try:
            ts = int(ts)
        except Exception:
            raise ValueError(f"Unable to convert object ({ts}) into a valid int or long item!")
    # check if can be converted
    if isinstance(ts, int):
        # convert to datetime
        dt = datetime.fromtimestamp(ts, tz=timezone("UTC"))
        if tz is not None:
            dt_result = localize_datetime(dt, tz)
            if dt_result is None:
                raise ValueError("Failed to localize datetime")
            dt = dt_result
        else:
            print("WARNING: No timezone given for timestamp, infering 'UTC' as default!")
        return dt
    raise ValueError(f"Given object ({ts}) is not a valid int or long item!")


def any_to_datetime(
    ts: str | datetime | date | Any, logger: Logger | None = None, date_format: str | None = None
) -> datetime | None:
    """Generates a safe datetime from the input information.

    Args:
        ts: object to convert to datetime
        logger: Logging object to output infos
        date_format: Optional string with the date format to use (otherwise will try common ones)

    Returns:
        `datetime` object if converted or `None`
    """
    dt = None

    # check if special case
    if ts is None or isinstance(ts, datetime):
        return ts

    # check if only date
    if isinstance(ts, date) and not isinstance(ts, datetime):
        dt = datetime.combine(ts, datetime.min.time())

    # convert from int or string
    if dt is None:
        with contextlib.suppress(Exception):
            dt = unix_to_datetime(ts)

    # try relevant string formats
    if dt is None and isinstance(ts, str):
        # check for empty string
        if not ts:
            return None

        # FEAT: improve list
        formats = DATE_FORMATS
        if date_format is not None:
            formats = [date_format, *formats]

        try:
            dt = parser.isoparse(ts)
        except Exception:
            # check all formats
            for fmt in formats:
                try:
                    dt = datetime.strptime(ts, fmt)
                    if logger is not None:
                        logger.info(f"Date-Format '{fmt}' worked")
                except Exception:
                    if logger is not None:
                        logger.info(f"Date-Format '{fmt}' did not work")

    # check if only date
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())

    # check for additional types
    if pd:
        if isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()
        if dt == pd.NaT:
            return None
    if np:
        if isinstance(dt, np.datetime64):
            dt = dt.astype(datetime)
        if dt == np.nan:
            return None

    if dt is None:
        raise ValueError(f"Unable to parse datetime ({ts})")

    return dt


def convert_to_datetime(
    dt: datetime | date | time, baseline: datetime | None = None, remove_tz: bool = False
) -> datetime:
    """Converts the given data to datetime.

    This might include conversions from date and time data-types

    Args:
        dt: Datetime, time or date object to convert
        baseline: datetime object to retrieve info from or None. Default is datetime.now()
        remove_tz: Defines if timezone information should be removed

    Returns:
        datetime object
    """
    # check baseline
    if baseline is None:
        baseline = datetime.now()

    # check for types
    if isinstance(dt, datetime):
        pass
    elif isinstance(dt, time):
        dt = datetime(baseline.year, baseline.month, baseline.day, dt.hour, dt.minute, dt.second)
    elif isinstance(dt, date):
        dt = datetime(dt.year, dt.month, dt.day, 12, 0)
    else:
        raise ValueError(f"Given datetime data has unkown type ({type(dt)}")

    # check for removal
    if remove_tz:
        dt = dt.replace(tzinfo=None)

    return dt


def localize_datetime(dt: datetime | None, tz: Any | str | timezone | None = None) -> datetime | None:
    """Localizes a datetime to the current timezone.

    Args:
        dt (datetime): Datetime to make aware
        tz (str, timezone): Timezone (either directly or name of the timezone)
    """
    # check if None
    if dt is None:
        return None
    if tz is None:
        tz = current_timezone()

    # update the timezone
    if isinstance(tz, str):
        tz = timezone(tz)

    # check if timezone should be added or converted
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def make_aware(
    dt: datetime | str | Any,
    tz: str | timezone | Any = None,
    force_convert: bool = True,
    col: str | None = None,
) -> datetime | Any:
    """Checks if the current datetime is aware, otherwise make aware.

    Args:
        dt (datetime, str, Any): Datetime to convert
        tz (str, ZoneInfo, Any): Name of the timezone to convert to
        force_convert (bool): Defines if the timezone should be converted if there is already a timezone present
        col (str, None): Column used if the input is pandas Dataframe

    Returns:
        Updated datetime (or pandas object)
    """
    # ensure that data is not none
    if dt is None:
        return None

    # check for pandas
    is_pandas = False
    with contextlib.suppress(NameError, TypeError):
        # Check if pandas types are available and dt is an instance
        is_pandas = isinstance(dt, (Series, DataFrame))

    if is_pandas:
        assert col is not None, "Column is required for pandas objects"
        return make_aware_pandas(dt, col, tz=tz)  # type: ignore[arg-type]

    # make sure dt is datetime
    dt = any_to_datetime(dt)
    if dt is None:
        return None

    # check if already aware
    if dt.tzinfo is not None and (tz is None or force_convert is False):
        return dt

    # check for local timezone (if none provided)
    if tz is None:
        tz = current_timezone()

    # return localized datetime
    return localize_datetime(dt, tz)


def make_aware_pandas(
    df: Series | DataFrame, col: str, format: str | None = None, tz: str | timezone | None = None
) -> Series | DataFrame:
    """This will make the pandas column datetime aware in the specified timezone.

    Defaults the data to the current timezone.

    Args:
        df: DataFrame to convert
        col: name of the column to convert
        format: Default format to try
        timezone: default timezone to convert to

    Returns:
        Updated DataFrame
    """
    # check if pandas is install
    if Series is None or DataFrame is None:
        raise ImportError("Pandas Library is not installed")

    # safty checks
    if df is None:
        return None
    if col is None:
        raise ValueError("Expected column name, but got None")
    if col not in df:
        raise RuntimeError(f"The specified column {col} is not available in the dataframe: {df.columns}")

    # make sure the data is unaware
    if not is_datetime(df[col]):
        # generate format list
        formats = []
        if format is not None:
            formats.append(format)
        formats.extend(DATE_FORMATS)

        # check all formats
        for fmt in formats:
            with contextlib.suppress(Exception):
                df[col] = to_datetime(df[col], format=fmt)

    # TODO: update timezone ensurances
    # ensure timezone
    if not hasattr(df[col].iloc[0], "tzinfo") or not df[col].iloc[0].tzinfo:
        cur_tz_obj = current_timezone()
        cur_tz = getattr(cur_tz_obj, "key", str(cur_tz_obj))
        try:
            df[col] = df[col].dt.tz_localize(cur_tz)
        except AmbiguousTimeError:
            infer_dst = nparray([False] * df.shape[0])
            df[col] = df[col].dt.tz_localize(cur_tz, ambiguous=infer_dst)
    if tz is not None:
        # convert to string (as pandas does not support ZoneInfo)
        if isinstance(tz, timezone):
            tz = tz.key
        df.loc[:, col] = df[col].dt.tz_convert(tz)

    return df


def make_unaware(dt: datetime | Any, tz: str | tzinfo | timezone = "UTC") -> datetime | None:
    """Makes the given timezone unaware in a default timezone.

    Args:
        dt: Datetime to convert
        tz: Timezone to convert to as basetime

    Returns:
        datetime object without timezone info
    """
    # ensure the datetime is safe
    dt = any_to_datetime(dt)

    # check against None values
    if dt is None:
        return None

    # convert the timezone
    result = localize_datetime(dt, tz)
    if result is None:
        return None
    return result.replace(tzinfo=None)
