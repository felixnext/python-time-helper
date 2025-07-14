from datetime import datetime, timedelta

from time_helper import time_to_interval


def test_time_to_interval():
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


def test_create_interval():
    # TODO: implement
    pass
