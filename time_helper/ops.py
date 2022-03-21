'''
Contains a range of operations on different datetimes.
'''

from datetime import datetime, date, timedelta
from typing import Union

try:
    from pandas import Series, DataFrame
    from pandas.api.types import (
        is_datetime64_any_dtype as is_datetime
    )
except Exception:
    Series = None
    DataFrame = None
    is_datetime = lambda x: False

from time_helper.convert import make_aware, any_to_datetime, localize_datetime


def has_timezone(df: Union[Series, DataFrame], col: str = None) -> bool:
    '''Checks if a given pandas object has a timezone.

    Args:

    '''
    # perform security
    if df is None:
        raise ValueError("Expected a dataframe but got None")
    if isinstance(df, DataFrame):
        if col is None:
            raise ValueError("Expected a column name, but got None")
        if col not in df.columns:
            raise ValueError(f"The provided column {col} is not in the dataframe {df.columns}")
        if not is_datetime(df[col]):
            raise ValueError("Specified column is not a datetime object!")
    elif not is_datetime(df):
        raise ValueError("Provided series is not a datetime object!")
    if len(df) == 0:
        raise ValueError("The Dataframe is empty")

    # perform checks
    df_col = df if isinstance(df, Series) else df[col]
    obj = df_col.iloc[0]
    if not hasattr(obj, 'tzinfo'):
        return False
    if obj.tzinfo is None:
        return False
    return True


def time_diff(dt1: datetime, dt2: datetime, tz=None) -> timedelta:
    '''Allows to compute the difference between datetimes of different timezones.

    Calculates dt1 - dt2

    Args:
        dt1 (datetime): First datetime in the diff
        dt2 (datetime): Second datetime in the diff
        tz (str): Name of the default timezone to use

    Returns:
        timedelta
    '''
    # check for unaware
    if dt1.tzinfo is None and dt2.tzinfo is None:
        return dt1 - dt2

    # update timezones
    if dt1.tzinfo is None:
        dt1 = make_aware(dt1, tz, force_convert=False)
    if dt2.tzinfo is None:
        dt2 = make_aware(dt2, tz, force_convert=False)

    # bring both datetimes to same timezone
    dt1 = localize_datetime(dt1, 'UTC')
    dt2 = localize_datetime(dt2, 'UTC')

    # calculate
    return dt1 - dt2


def round_time(dt: datetime, freq: str = "D", max_out: bool = False) -> datetime:
    '''Rounds the given timestamp to the start or end of the day.

    Args:
        timestamp (datetime): Datetime that should be rounded
        freq (str): Frequency to round it to (options are S, M, H, D, W, m, Y)
        max_out (bool): Defines if remaining attributes should be zeroed (False) or maxed out (True)

    Returns:
        Updated datetime
    '''
    # check if value is provided
    if not dt:
        return None

    # ensure value is a datetime
    if not isinstance(dt, datetime):
        try:
            dt = any_to_datetime(dt)
        except Exception:
            raise ValueError(f"Could not parse Timestamp: {dt}")

    # check for date
    if not isinstance(dt, datetime) and isinstance(dt, date) and freq in ["H", "M", "S"]:
        raise ValueError("Got a date, but frequency requires datetime")

    # check for week special case
    if freq == "W":
        day = dt.weekday()
        dt = dt + timedelta(days=6 - day) if max_out else dt - timedelta(days=day)

    # update time to get most out of day
    items = {"microsecond": 999999 if max_out else 0}
    if freq not in ["S"]:
        items["second"] = 59 if max_out else 0
    if freq not in ["S", "M"]:
        items["minute"] = 59 if max_out else 0
    if freq not in ["S", "M", "H"]:
        items["hour"] = 23 if max_out else 0
    if freq in ["Y", "m"]:
        day_in_month = (dt.replace(month=dt.month % 12 + 1, day=1) - timedelta(days=1)).day
        items["day"] = day_in_month if max_out else 1
    if freq in ["Y"]:
        items["month"] = 12 if max_out else 1
        items["day"] = 31 if max_out else items["day"]
    dt = dt.replace(**items)

    return dt
