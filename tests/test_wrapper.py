'''Test Code for the wrapper class'''

from datetime import tzinfo, datetime
import time

try:
    import zoneinfo
except ImportError:
    import backports.zoneinfo as zoneinfo

from time_helper import DateTimeWrapper, localize_datetime

def test_create():
    '''Tests the creation of various wrapper classes'''
    # check the basic creation from datetime and equality checks
    dt = datetime.now()
    wt = DateTimeWrapper(dt)

    assert wt == dt
    assert wt() == dt
    # negative check
    time.sleep(0.5)
    assert wt != datetime.now()

    # test creation of datetimes
    wt = DateTimeWrapper(dt, "Asia/Kolkata")
    assert wt == localize_datetime(dt, "Asia/Kolkata")


def test_call():
    '''Tests if inner datetime objects are mapped to the corret functions.'''
    # get a datetime
    dt = datetime(2022, 10, 19, 12, 00)
    wt = DateTimeWrapper(dt)

    # compare data
    wt.isoformat()
