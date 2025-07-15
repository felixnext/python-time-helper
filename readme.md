# Time Helper

A lightweight Python library for effortless datetime handling with timezone support. Built for simplicity and flexibility, it provides a comprehensive set of utilities for parsing, converting, and manipulating dates and times.

**Key Features:**
- 🌍 **Timezone-aware operations** with abbreviation support (e.g., IST, PST, CET)
- 🔄 **Universal datetime parsing** from strings, timestamps, and various formats
- 📊 **Optional pandas/numpy integration** for DataFrame operations
- 🎯 **Simple, intuitive API** with one-line conversions
- 🐍 **Modern Python 3.10+** with full type hints

## Installation

### Basic Installation

For core datetime functionality without heavy dependencies:

```bash
# Using pip
pip install time-helper

# Using uv (recommended)
uv add time-helper
```

### With Optional Dependencies

Add pandas and/or numpy support for DataFrame operations and advanced array handling:

```bash
# With pandas support (includes DataFrame/Series datetime operations)
pip install time-helper[pandas]
uv add time-helper[pandas]

# With numpy support (for numpy datetime64 conversions)
pip install time-helper[numpy]
uv add time-helper[numpy]

# With both pandas and numpy
pip install time-helper[pandas,numpy]
uv add time-helper[pandas,numpy]
```

## Quick Start

```python
from time_helper import any_to_datetime, make_aware, round_time

# Parse any datetime format automatically
dt = any_to_datetime("2024-03-15 10:30:45")
dt = any_to_datetime(1710501045)  # Unix timestamp
dt = any_to_datetime("15/03/2024", date_format="%d/%m/%Y")

# Make timezone-aware (auto-detects system timezone)
aware_dt = make_aware("2024-03-15")
# > datetime.datetime(2024, 3, 15, 0, 0, tzinfo=ZoneInfo('America/New_York'))

# Convert between timezones using abbreviations
from time_helper import localize_datetime
tokyo_time = localize_datetime(aware_dt, "JST")  # Japan Standard Time
delhi_time = localize_datetime(aware_dt, "IST")  # Indian Standard Time

# Round to nearest hour, day, week, etc.
rounded = round_time(dt, "H")  # Hour
rounded = round_time(dt, "D", max_out=True)  # End of day (23:59:59.999999)
```

## Features

### 🔄 Universal DateTime Parsing

The `any_to_datetime` function intelligently parses various datetime formats:

```python
from time_helper import any_to_datetime
from datetime import date

# Parse different formats automatically
dt = any_to_datetime("2024-03-19")                    # ISO date
dt = any_to_datetime("2024-03-19 20:15:30")          # ISO datetime
dt = any_to_datetime("19/03/2024", date_format="%d/%m/%Y")  # Custom format
dt = any_to_datetime(1710501045)                      # Unix timestamp
dt = any_to_datetime(date(2024, 3, 19))              # Python date object
dt = any_to_datetime("2024-03-19T15:30:00.123Z")     # ISO with milliseconds
```

### 🌍 Timezone Operations

Seamlessly work with timezones using names or abbreviations:

```python
from time_helper import make_aware, make_unaware, localize_datetime, current_timezone

# Auto-detect system timezone
current_tz = current_timezone()

# Make timezone-aware using system timezone
aware_dt = make_aware("2024-03-15")

# Explicit timezone
utc_dt = make_aware("2024-03-15", "UTC")
tokyo_dt = make_aware("2024-03-15", "Asia/Tokyo")

# Use timezone abbreviations (automatically mapped)
ist_dt = make_aware("2024-03-15", "IST")  # Maps to Asia/Kolkata
pst_dt = make_aware("2024-03-15", "PST")  # Maps to America/Los_Angeles

# Convert between timezones
ny_time = localize_datetime(utc_dt, "America/New_York")
berlin_time = localize_datetime(utc_dt, "Europe/Berlin")

# Remove timezone information
unaware_dt = make_unaware(aware_dt)  # Keeps the time as-is
unaware_utc = make_unaware(berlin_time, "UTC")  # Converts to UTC first
```

### ⏰ DateTime Operations

Powerful operations for datetime manipulation:

```python
from time_helper import round_time, time_diff

# Round to various frequencies
dt = any_to_datetime("2024-03-15 14:35:27.123456")

# Round down (floor)
hour_start = round_time(dt, "H")    # 2024-03-15 14:00:00
day_start = round_time(dt, "D")     # 2024-03-15 00:00:00
week_start = round_time(dt, "W")    # 2024-03-11 00:00:00 (Monday)
month_start = round_time(dt, "m")   # 2024-03-01 00:00:00
year_start = round_time(dt, "Y")    # 2024-01-01 00:00:00

# Round up (ceiling) with max_out=True
hour_end = round_time(dt, "H", max_out=True)   # 2024-03-15 14:59:59.999999
day_end = round_time(dt, "D", max_out=True)     # 2024-03-15 23:59:59.999999
week_end = round_time(dt, "W", max_out=True)    # 2024-03-17 23:59:59.999999

# Calculate timezone-aware differences
tokyo = make_aware("2024-03-15 10:00", "Asia/Tokyo")
london = make_aware("2024-03-15 10:00", "Europe/London")
diff = time_diff(tokyo, london)  # -9 hours difference
```

### 📊 Pandas Integration (Optional)

When pandas is installed, additional DataFrame operations become available:

```python
import pandas as pd
from time_helper import make_aware, has_timezone

# Create sample DataFrame
df = pd.DataFrame({
    'timestamp': ['2024-03-15 10:00', '2024-03-16 15:30'],
    'event': ['start', 'end']
})

# Make timezone-aware
df = make_aware(df, col='timestamp', tz='UTC')

# Check timezone presence
has_tz = has_timezone(df, 'timestamp')  # True

# Convert timezone
df = make_aware(df, col='timestamp', tz='America/New_York')
```

### 📈 Time Range Operations

Create and manipulate time intervals:

```python
from time_helper import create_intervals, time_to_interval
from datetime import datetime, timedelta

start = datetime(2024, 3, 15, 9, 0)
end = datetime(2024, 3, 15, 17, 0)

# Create hourly intervals
hourly = create_intervals(start, end, interval=timedelta(hours=1))
# [(datetime(2024, 3, 15, 9, 0), datetime(2024, 3, 15, 10, 0)),
#  (datetime(2024, 3, 15, 10, 0), datetime(2024, 3, 15, 11, 0)), ...]

# Convert time to position in day (0.0 = midnight, 0.5 = noon)
noon = datetime(2024, 3, 15, 12, 0)
pos = time_to_interval(noon, offset=0)  # 0.0 (noon centered)
pos = time_to_interval(noon, offset=0, zero_center=False)  # 0.5
```

## Development

Install for development with all optional dependencies:

```bash
# Clone the repository
git clone https://github.com/felixnext/python-time-helper.git
cd python-time-helper

# Install with all extras using uv
uv sync --all-extras

# Run tests
uv run pytest

# Run linting and type checking
uv run ruff check .
uv run mypy time_helper
```

## DateTimeWrapper

The library includes a `DateTimeWrapper` class that provides a fluent, object-oriented interface for datetime operations:

```python
from time_helper import DateTimeWrapper

# Create wrapper from various inputs
dtw = DateTimeWrapper("2024-03-15 10:30:00")
dtw = DateTimeWrapper(datetime.now())
dtw = DateTimeWrapper(date(2024, 3, 15))
dtw = DateTimeWrapper(1710501045)  # Unix timestamp

# Chainable operations
result = (DateTimeWrapper("2024-03-15 10:35:45")
          .make_aware("UTC")
          .round("H")
          .localize("Asia/Tokyo")
          .to_string("%Y-%m-%d %H:%M %Z"))

# Arithmetic operations
tomorrow = dtw + timedelta(days=1)
yesterday = dtw - timedelta(days=1)
diff = tomorrow - yesterday  # Returns timedelta

# Comparison operations
if dtw > DateTimeWrapper("2024-01-01"):
    print("After new year")

# Direct property access
print(f"Year: {dtw.year}, Month: {dtw.month}, Day: {dtw.day}")
print(f"Weekday: {dtw.weekday}")  # 0=Monday, 6=Sunday

# Timezone operations
aware = dtw.make_aware("EST")
unaware = aware.make_unaware()
tokyo = aware.localize("Asia/Tokyo")

# String conversion
iso_str = dtw.to_string()  # ISO format
custom_str = dtw.to_string("%B %d, %Y")  # "March 15, 2024"
unix_ts = dtw.to_timestamp()  # Unix timestamp
```

## DST Support

The library includes comprehensive Daylight Saving Time (DST) support for handling timezone transitions:

```python
from time_helper import is_dst_active, get_dst_transitions, next_dst_transition, make_aware

# Check if DST is currently active
summer_time = make_aware("2024-07-15 12:00:00", "Europe/Berlin")
is_dst_active(summer_time)  # True (CEST is active)

winter_time = make_aware("2024-01-15 12:00:00", "Europe/Berlin")
is_dst_active(winter_time)  # False (CET is active)

# Get all DST transitions for a timezone in a given year
transitions = get_dst_transitions("Europe/Berlin", 2024)
# [
#   {"type": "spring_forward", "date": datetime(2024, 3, 31, 2, 0, ...)},
#   {"type": "fall_back", "date": datetime(2024, 10, 27, 3, 0, ...)}
# ]

# Find the next DST transition from a given datetime
winter_dt = make_aware("2024-02-15 12:00:00", "Europe/Berlin")
next_trans = next_dst_transition(winter_dt)
# {"type": "spring_forward", "date": datetime(2024, 3, 31, 2, 0, ...)}

summer_dt = make_aware("2024-07-15 12:00:00", "Europe/Berlin")
next_trans = next_dst_transition(summer_dt)
# {"type": "fall_back", "date": datetime(2024, 10, 27, 3, 0, ...)}
```

**DST Features:**
- Automatic handling of "spring forward" and "fall back" transitions
- Support for ambiguous times (when clocks fall back)
- Robust handling of non-existent times (when clocks spring forward)
- Works with all timezone databases that support DST

## Natural Language Parsing

The library supports parsing natural language datetime expressions for intuitive date and time manipulation:

```python
from time_helper import parse_natural, DateTimeWrapper
from datetime import datetime

# Basic relative expressions
ref_date = datetime(2024, 7, 15, 12, 0, 0)  # Monday, July 15, 2024

# Time references
now = parse_natural("now")
today = parse_natural("today", reference=ref_date)
tomorrow = parse_natural("tomorrow", reference=ref_date)
yesterday = parse_natural("yesterday", reference=ref_date)

# Weekday references
monday = parse_natural("monday", reference=ref_date)  # Current Monday
next_monday = parse_natural("next monday", reference=ref_date)  # Next Monday
last_friday = parse_natural("last friday", reference=ref_date)  # Previous Friday

# Time expressions
morning = parse_natural("morning", reference=ref_date)  # 9:00 AM
afternoon = parse_natural("afternoon", reference=ref_date)  # 2:00 PM
evening = parse_natural("evening", reference=ref_date)  # 7:00 PM
night = parse_natural("night", reference=ref_date)  # 10:00 PM

# Specific times
nine_am = parse_natural("9am", reference=ref_date)
two_thirty_pm = parse_natural("2:30pm", reference=ref_date)
noon = parse_natural("noon", reference=ref_date)
midnight = parse_natural("midnight", reference=ref_date)

# Complex expressions
tomorrow_9am = parse_natural("tomorrow at 9am", reference=ref_date)
next_week = parse_natural("next week", reference=ref_date)
last_month = parse_natural("last month", reference=ref_date)

# Relative time offsets
in_2_hours = parse_natural("in 2 hours", reference=ref_date)
in_30_minutes = parse_natural("in 30 minutes", reference=ref_date)
2_days_ago = parse_natural("2 days ago", reference=ref_date)
1_week_ago = parse_natural("1 week ago", reference=ref_date)

# Business day references
next_business_day = parse_natural("next business day", reference=ref_date)
last_business_day = parse_natural("last business day", reference=ref_date)

# Weekend references
this_weekend = parse_natural("this weekend", reference=ref_date)
next_weekend = parse_natural("next weekend", reference=ref_date)

# Date boundaries
beginning_of_month = parse_natural("beginning of month", reference=ref_date)
end_of_month = parse_natural("end of month", reference=ref_date)
beginning_of_year = parse_natural("beginning of year", reference=ref_date)
end_of_year = parse_natural("end of year", reference=ref_date)

# Ordinal expressions
first_of_month = parse_natural("first of the month", reference=ref_date)
15th_next_month = parse_natural("15th of next month", reference=ref_date)
```

### Natural Language with DateTimeWrapper

The `DateTimeWrapper` class supports natural language parsing and provides additional methods for natural language operations:

```python
from time_helper import DateTimeWrapper
from datetime import timedelta

# Create wrapper with natural language
dtw = DateTimeWrapper("tomorrow at 9am")
dtw = DateTimeWrapper("next monday")
dtw = DateTimeWrapper("in 2 hours")

# Chain operations with natural language
result = (DateTimeWrapper("tomorrow at 9am")
          .make_aware("UTC")
          .round("H")
          .localize("Asia/Tokyo"))

# Use natural language parsing with timedelta for offsets
dtw = DateTimeWrapper("2024-07-15 12:00:00")
tomorrow = dtw + timedelta(days=1)
next_week = dtw + timedelta(weeks=1)
in_2_hours = dtw + timedelta(hours=2)
```

**Supported Natural Language Patterns:**
- Time references: "now", "today", "tomorrow", "yesterday"
- Weekdays: "monday", "tuesday", etc. with "next" and "last" modifiers
- Time of day: "morning", "afternoon", "evening", "night", "noon", "midnight"
- Specific times: "9am", "2:30pm", "14:30"
- Time ranges: "this weekend", "next weekend", "next week", "last month"
- Relative offsets: "in 2 hours", "3 days ago", "1 week ago"
- Business days: "next business day", "last business day"
- Date boundaries: "beginning of month", "end of year"
- Ordinals: "first of the month", "15th of next month"
- Complex expressions: "tomorrow at 9am", "next monday at 2:30pm"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
