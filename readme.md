# Time Helper

Simple helper library to handle different time related tasks in python. This ties into pandas and numpy as well as pytz.

The general idea is to have a bunch of one-stop functions that allow you to easily handle datetime related tasks.

## Getting Started

```bash
pip install time-helper
```

Then in python code:

```python
from time_helper import make_aware

make_aware("2022-03-10")
# > datetime.datetime(2022, 3, 10, 0, 0, tzinfo=backports.zoneinfo.ZoneInfo(key='CET'))
```

## Library Logic

The library is build to extend around various datetime objects (such as python internal datetime, date, as well as np.datetime).
It provides a bunch of helper functions that are grouped into various categories:

### Convert

This gets datetimes in and out of the library. This includes a range of functions for converting strings and different datetime types into canonical py-datetime types:

```python
import time_helper as th

# convert a unix datetime
dt = th.unix_to_datetime(1649491287)
dt = th.any_to_datetime(1649491287)

# convert string to datetime
dt = th.any_to_datetime("2022-03-19")
dt = th.any_to_datetime("2022-03-19 20:15")

# convert a date to datetime
from datetime import date
dt = th.any_to_datetime(date(2022, 3, 10))
```

It also allows to easily switch between aware and unaware datetime:

```python
dt = th.any_to_datetime("2022-03-10")
aware_dt = th.make_aware(dt)
aware_dt = th.make_aware(dt, "UTC")
unaware_dt = th.make_unaware(dt)
unaware_dt = th.make_unaware(dt, "UTC")
```

Note that for `make_unaware` you can still provide a datetime. In that case the datetime is first converted into the regarding timezone before the
timezone information is removed from the object. You can also explicitly convert the timezone with `localize_datetime`.

### Operations & Ranges

The library also defines a range of operations to make working with timezones easier.
These include handling modifications of a single datetime:

```python
day = th.round_time(dt, "D")
# results in: datetime.datetime(2022, 3, 10, 0, 0)
day = th.round_time(dt, "D", max_out=True)
# results in: datetime.datetime(2022, 3, 10, 23, 59, 59, 999999)
has_tz = th.has_timezone(aware_dt)
has_tz = th.has_timezone(unaware_dt)

# compute a diff (between aware and unaware datetimes)
diff = th.time_diff(
    th.round_time(aware_dt, "M", max_out=True),
    unaware_dt
)
# results in: datetime.timedelta(seconds=3659, microseconds=999999)
```

It also supports a bunch of range operations:

```python
# converts the time into a interval (float) value for the defined range
# default i
dt = datetime(2022, 3, 12, 12, 0)
pos = th.time_to_interval(dt, offset=0)
# results in: 0.0 (as it is noon)
pos = th.time_to_interval(dt, offset=0, zero_center=False)
# results in: 0.5 (as half day is gone and center is no longer zeroed)

# create interval tuples
ivs = th.create_intervals(dt, dt + timedelta(days=2), interval=1)
ivs = th.create_intervals(dt, dt + timedelta(days=2), interval=timedelta(minutes=30))
```

### Wrapper

This library also provides a wrapper class to make all functions more accessible and first class citizens of the system.

> **Note:** This part of the library is still under construction.

## Notes

There is still a lot to improve on this library, please feel free to create PRs or contact me if you wish to contribute!
