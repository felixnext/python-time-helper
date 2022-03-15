'''Various functions to handle time management'''

from datetime import datetime, date, timedelta, tzinfo, time
from dateutil import relativedelta, parser, rrule
from dateutil.rrule import WEEKLY

try:
    from zoneinfo import ZoneInfo as timezone
except ImportError:
    from backports.zoneinfo import ZoneInfo as timezone
import numpy as np
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype as is_datetime
)
from pytz import AmbiguousTimeError


DATE_FORMATS = ['%Y-%m-%d %H:%M:%S.%f', '%Y.%m.%d %H:%M:%S', '%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y', '%m/%d/%y', '%m.%d.%Y', '%d.%m.%Y']


def find_timezone(name):
    '''Retrieves the given timezone by name.'''
    # check if already converted
    if isinstance(name, tzinfo):
        return name

    # try to convert
    try:
        return timezone(name)
    except Exception:
        return None


def current_timezone():
    '''Retrieves the currently active timezone.'''
    return timezone(datetime.now().astimezone().tzname())


def localize_datetime(dt, tz=None):
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
    else:
        return dt.astimezone(tz)


def make_aware(dt, tz=None, force_convert=True):
    '''Checks if the current datetime is aware, otherwise make aware.

    Args:
        dt (datetime): Datetime to convert
        tz (str): Name of the timezone to convert to
        force_convert (bool): Defines if the timezone should be converted if there is already a timezone present
    '''
    # ensure that data is not none
    if dt is None:
        return None

    # make sure dt is datetime
    dt = safe_datetime(dt)

    # check if already aware
    if dt.tzinfo is not None and (tz is None or force_convert is False):
        return dt

    # check for local timezone (if none provided)
    if tz is None:
        tz = current_timezone()

    # return localized datetime
    return localize_datetime(dt, tz)


def make_aware_pandas(df, col, format=None, tz=None):
    '''This will make the pandas column datetime aware in the specified timezone.

    Defaults the data to the current timezone.

    Args:
        df: DataFrame to convert
        col: name of the column to convert
        format: Default format to try
        timezone: default timezone to convert to

    Returns:
        Updated DataFrame
    '''
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
        formats.append(None)
        formats += DATE_FORMATS

        # check all formats
        for fmt in formats:
            try:
                df[col] = pd.to_datetime(df[col], format=fmt)
            except Exception:
                pass

    # ensure timezone
    if not has_timezone_pandas(df, col):
        cur_tz = current_timezone().key
        try:
            df[col] = df[col].dt.tz_localize(cur_tz)
        except AmbiguousTimeError:
            infer_dst = np.array([False] * df.shape[0])
            df[col] = df[col].dt.tz_localize(cur_tz, ambiguous=infer_dst)
    if tz is not None:
        # convert to string (as pandas does not support ZoneInfo)
        if isinstance(tz, timezone):
            tz = tz.key
        df.loc[:, col] = df[col].dt.tz_convert(tz)

    return df


def has_timezone_pandas(df, col):
    # perform security
    if df is None:
        raise ValueError("Expected a dataframe but got None")
    if col is None:
        raise ValueError("Expected a column name, but got None")
    if col not in df.columns:
        raise ValueError(f"The provided column {col} is not in the dataframe {df.columns}")
    if len(df) == 0:
        raise ValueError("The Dataframe is empty")
    if not is_datetime(df[col]):
        raise ValueError("Specified column is not a datetime object!")

    # perform checks
    obj = df[col].iloc[0]
    if not hasattr(obj, 'tzinfo'):
        return False
    if obj.tzinfo is None:
        return False
    return True


def make_unaware(dt, tz="UTC"):
    '''Makes the given timezone unaware in a default timezone.'''
    # check against None values
    if dt is None:
        return None

    # ensure the datetime is safe
    dt = safe_datetime(dt)

    # convert the timezone
    return localize_datetime(dt, tz).replace(tzinfo=None)


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


def safe_datetime(ts, logger=None, date_format=None):
    '''Generates a safe datetime from the input information.

    Args:
        ts: object to convert to datetime
        logger: Logging object to output infos
        date_format: Optional string with the date format to use (otherwise will try common ones)

    Returns:
        `datetime` object if converted or `None`
    '''
    dt = None

    # check if special case
    if ts is None or isinstance(ts, datetime):
        return ts

    # convert from int or string
    try:
        dt = unix_to_datetime(ts)
    except Exception:
        pass

    # try relevant string formats
    if dt is None and isinstance(ts, str):
        # FEAT: improve list
        formats = DATE_FORMATS
        if date_format is not None:
            formats = [date_format] + formats

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
    if isinstance(dt, date):
        dt = datetime.combine(dt, datetime.min.time())

    if dt is None:
        raise ValueError(f"Unable to parse datetime ({ts})")

    return dt


def unix_to_datetime(ts, tz=None):
    '''Converts the given objects into a datetime.

    Args:
        ts: `int` or `long` that contains the timestamp
        tz: `pytz.timezone` that is used for localization

    Returns:
        `datetime` object that contains the time
    '''
    # check if should be parsed
    if isinstance(ts, str):
        try:
            ts = int(ts)
        except Exception:
            pass
    # check if can be converted
    if isinstance(ts, int):
        # convert to datetime
        dt = datetime.utcfromtimestamp(ts)
        dt = dt.replace(tzinfo=timezone("UTC"))
        if tz is not None:
            dt = localize_datetime(dt, tz)
        else:
            print("WARNING: No timezone given for timestamp, infering 'UTC' as default!")
        return dt
    else:
        raise ValueError("Given object ({}) is not a valid int or long item!".format(ts))


def parse_time(time_str, format, timezone):
    '''Parses the given time based on the format and timezone (if provdied).

    Returns:
        (timzone-aware) datetime object
    '''
    # check the current timezone
    timezone = find_timezone(timezone)

    # update
    if isinstance(time_str, datetime):
        dt = time_str
    else:
        dt = datetime.strptime(time_str, format)
    if timezone is not None:
        dt = dt.replace(tzinfo=timezone)
    return dt


def convert_to_datetime(dt, baseline=None, remove_tz=False):
    '''Converts the given data to datetime.

    This might include conversions from date and time data-types

    Args:
        dt: Datetime, time or date object to convert
        baseline: datetime object to retrieve info from or None. Default is datetime.now()
        remove_tz: Defines if timezone information should be removed

    Returns:
        datetime object
    '''
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


def time_to_interval(dt, offset: int = 12, baseline=None, zero_center=True, normalize=True):
    '''Converts a datetime value into an interval along the day.

    In case of normalization the data is ranged from 0 to 1 (for the timestamp +- offset)
    If zero_center is enabled this range shifts to [-.5, .5]

    Args:
        dt: The datetime to convert
        offset: Number of hours to add to both ends to avoid errors due to overcasts.
            This can also be a tuple to have asymmetric offset
        baseline: Datetime that is used as baseline (if None take day from the dt)
        zero_center: Defines if the middle of the time range should be 0 centered
            (meaning everything before is negative values)

    Returns:
        Float value of the time position - if normalized a value between 0 and 1 (1 = last possible time) - otherwise a value in minutes
    '''
    # convert to unaware
    dt_base = convert_to_datetime(baseline, None, True) if baseline else None
    dt_uw = convert_to_datetime(dt, baseline, True)
    dt_base = baseline if baseline else dt_uw

    # retrieve offset
    if isinstance(offset, tuple) or isinstance(offset, list):
        offset_start = offset[0]
        offset_end = offset[1]
    else:
        offset_start = offset
        offset_end = offset

    # compute the total time
    total_min = (24 + offset_start + offset_end) * 60
    total_end = datetime(dt_base.year, dt_base.month, dt_base.day, 23, 59) + timedelta(hours=offset_end, minutes=1)

    # measure time by distance to the total end
    dt_min = total_min - ((total_end - dt_uw).total_seconds() / 60)

    # check for centering
    if zero_center:
        dt_min -= (total_min / 2)

    # check for normalization
    if normalize:
        dt_min /= total_min

    return dt_min


def round_day(timestamp, end=False):
    '''Rounds the given timestamp to the start or end of the day.'''
    if not timestamp:
        return None
    if isinstance(timestamp, str):
        try:
            timestamp = safe_datetime(timestamp)
        except Exception:
            raise ValueError(f"Could not parse Timestamp: {timestamp}")

    # update time to get most out of day
    if end:
        timestamp = timestamp.replace(hour=23, minute=59, second=59)
    else:
        timestamp = timestamp.replace(hour=0, minute=0, second=0)

    return timestamp


def create_intervals(start, end=None, interval=6, round_days=False, skip=timedelta(seconds=1)):
    '''Generates an array of interval tuples for the given date range.

    Args:
        start (datetime): The to start at
        end (datetime): The time to end at
        interval_days (int): Number of days for each interval (or timedelta)
        round_days (bool): If the time from the input should be preserved or rounded to whole days

    Returns:
        List of datetime tuples (note that these are timezone aware) of start and end date
    '''
    # update the start and end dates
    start_date = safe_datetime(start)
    end_date = datetime.utcnow() if end is None else safe_datetime(end)
    if round_days:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    # check interval
    if not isinstance(interval, timedelta):
        if isinstance(interval, int) or isinstance(interval, float):
            interval = timedelta(days=interval)
        else:
            raise ValueError("Invalid interval passed")

    # convert to range
    date_range = []
    d_start = start_date
    while d_start < end_date:
        # update new item
        d_end = min(end_date, d_start + interval)
        if d_end - d_start > skip:
            date_range.append((d_start, d_end))

        # update the time
        d_start = d_start + interval

    return date_range


def get_intervals(start, end, freq, round_dates=False):
    '''Retrieves the intervals for the given start/end combination on the given freq.

    Args:
        start (datetime): Start Datetime
        end (datetime): End datetime (if none use now)
        freq (str): Frequency that can be "D", "W" or "M" (for weekly, daily, monthly)

    Returns:
        List of tuples with the regarding ranges
    '''
    if not end:
        end = datetime.now()
    # TODO: implement
    return []


def get_freq_name(dt, freq):
    '''Retrieves the name for the current date based on the frequency.

    Args:
        dt (datetime): Datetime to analyze
        freq (str): Frequency that can be "D", "W" or "M" (for weekly, daily, monthly)

    Returns:
        String name
    '''
    pass
