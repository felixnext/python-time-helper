'''
This contains all range operations (such as intervals).
'''

from datetime import timedelta, datetime

from time_helper import convert_to_datetime, any_to_datetime


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
    start_date = any_to_datetime(start)
    end_date = datetime.utcnow() if end is None else any_to_datetime(end)
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