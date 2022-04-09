# Time Helper

Simple helper library to handle different time related tasks in python. This ties into pandas and numpy as well as pytz.

The general idea is to have a bunch of one-stop functions that allow you to easily handle datetime related tasks.

## Getting Started

```bash
$ pip install time-helper
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

```

### Operations & Ranges

pass

### Timezone

Helps to handle timezone awareness

### Wrapper

This library also provides a wrapper class to make all functions more accessible and first class citizens of the system


## Examples

Here are a few examples on how this library can be used in praxis:
