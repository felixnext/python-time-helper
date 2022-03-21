# Time Helper

Simple helper library to handle different time related tasks in python. This ties into pandas and numpy as well as pytz.

## Getting Started

```bash
$ pip install time-helper
```

Then in python code:

```python
from time_helper import make_aware

make_aware("2022-03-10")
# results in: TODO
```

## Library Logic

The library is build to extend around various datetime objects (such as python internal datetime, date, as well as np.datetime).
It provides a bunch of helper functions that are grouped into various categories:

### Convert

This gets datetimes in and out of the library.

### Operations & Ranges

pass

### Timezone

Helps to handle timezone awareness

### Wrapper

This library also provides a wrapper class to make all functions more accessible and first class citizens of the system


## Examples

Here are a few examples on how this library can be used in praxis:
