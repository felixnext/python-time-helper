from datetime import datetime, timedelta

from time_helper import time_to_interval


def test_time_to_interval() -> None:
    """Tests if the conversion is correct"""
    dt = datetime(2020, 9, 23, 12, 00)
    iv = time_to_interval(dt, 0)
    assert iv == 0

    iv = time_to_interval(dt, 0, zero_center=False, normalize=True)
    assert iv == 0.5

    iv = time_to_interval(dt, 12)
    assert iv == 0

    iv = time_to_interval(dt, 12, zero_center=False, normalize=True)
    assert iv == 0.5

    iv = time_to_interval(dt, 12, zero_center=False, normalize=False)
    assert iv == 24 * 60

    # test time after the day
    dt = datetime(2020, 9, 24, 6, 00)
    base = dt - timedelta(hours=12)
    assert base.day == 23

    iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=True)
    assert iv == 42 / 48

    iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=False)
    assert iv == 42 * 60

    iv = time_to_interval(dt, 12, baseline=base, zero_center=True, normalize=True)
    assert iv == 18 / 48

    # test time before the day
    dt = datetime(2020, 9, 22, 22, 00)
    base = dt + timedelta(hours=12)
    assert base.day == 23

    iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=True)
    assert iv == 10 / 48

    iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=False)
    assert iv == 10 * 60

    iv = time_to_interval(dt, 12, baseline=base, zero_center=True, normalize=True)
    assert iv == -14 / 48

    # test async offset
    dt = datetime(2020, 9, 24, 6, 00)
    base = dt - timedelta(hours=12)
    assert base.day == 23

    iv = time_to_interval(dt, (6, 12), baseline=base, zero_center=False, normalize=True)
    assert iv == 36 / 42

    iv = time_to_interval(dt, (12, 6), baseline=base, zero_center=False, normalize=False)
    assert iv == 42 * 60

    iv = time_to_interval(dt, (6, 12), baseline=base, zero_center=False, normalize=False)
    assert iv == 36 * 60

    iv = time_to_interval(dt, (6, 12), baseline=base, zero_center=True, normalize=True)
    assert iv == 15 / 42

    # Test list-based offset (should work same as tuple)
    iv = time_to_interval(dt, [6, 12], baseline=base, zero_center=False, normalize=True)
    assert iv == 36 / 42


def test_create_interval() -> None:
    """Test create_intervals function."""
    from time_helper import create_intervals

    # Test basic interval creation
    start = datetime(2024, 1, 1, 10, 0)
    end = datetime(2024, 1, 3, 14, 0)

    # Test with 1 day intervals
    intervals = create_intervals(start, end, interval=1)
    assert len(intervals) == 3
    assert intervals[0][0] == start
    assert intervals[0][1] == datetime(2024, 1, 2, 10, 0)
    assert intervals[1][0] == datetime(2024, 1, 2, 10, 0)
    assert intervals[1][1] == datetime(2024, 1, 3, 10, 0)
    assert intervals[2][0] == datetime(2024, 1, 3, 10, 0)
    assert intervals[2][1] == end

    # Test with timedelta intervals
    intervals = create_intervals(start, end, interval=timedelta(hours=12))
    assert len(intervals) == 5
    assert intervals[0][0] == start
    assert intervals[0][1] == datetime(2024, 1, 1, 22, 0)

    # Test with float interval
    intervals = create_intervals(start, end, interval=0.5)  # 12 hours
    assert len(intervals) == 5
    assert intervals[0][0] == start
    assert intervals[0][1] == datetime(2024, 1, 1, 22, 0)

    # Test with round_days=True
    intervals = create_intervals(start, end, interval=1, round_days=True)
    assert len(intervals) == 3
    assert intervals[0][0] == datetime(2024, 1, 1, 0, 0)
    assert intervals[0][1] == datetime(2024, 1, 2, 0, 0)
    assert intervals[2][1] == datetime(2024, 1, 3, 23, 59, 59, 999999)

    # Test with no end date (should use current time)
    intervals = create_intervals(start, interval=1)
    assert len(intervals) > 0
    assert intervals[0][0] == start

    # Test with custom skip parameter
    start_short = datetime(2024, 1, 1, 10, 0)
    end_short = datetime(2024, 1, 1, 10, 30)
    intervals = create_intervals(start_short, end_short, interval=timedelta(minutes=10), skip=timedelta(minutes=5))
    assert len(intervals) == 3

    # Test with skip that filters out small intervals
    intervals = create_intervals(start_short, end_short, interval=timedelta(minutes=10), skip=timedelta(minutes=20))
    assert len(intervals) == 0  # All intervals are <= 20 minutes, so filtered out

    # Test error handling
    try:
        create_intervals(None)
        raise AssertionError("Should raise ValueError for None start")
    except ValueError:
        pass

    try:
        create_intervals(start, "invalid_end")
        raise AssertionError("Should raise ValueError for invalid end")
    except ValueError as e:
        assert "Unable to parse datetime" in str(e) or "Failed to parse end date" in str(e)

    try:
        create_intervals(start, end, interval="invalid")  # type: ignore[arg-type]
        raise AssertionError("Should raise ValueError for invalid interval")
    except ValueError:
        pass
