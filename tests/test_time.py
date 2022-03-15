'''Various Unit-Tests regarding time.'''


import os
import sys
import unittest
from datetime import datetime, timedelta, tzinfo
import zoneinfo
import pandas as pd

# setup the root folder and add to path
ROOT_FOLDER = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(ROOT_FOLDER)
from time_helper import (
    find_timezone,
    current_timezone,
    localize_datetime,
    make_aware,
    make_unaware,
    time_diff,
    parse_time,
    unix_to_datetime,
    has_timezone_pandas,
    make_aware_pandas,
    time_to_interval
)


# NOTE: this might needs to be adjusted
LOCAL_TZ = "CET"


class UtilsTimeTest(unittest.TestCase):
    def test_findtz(self):
        tz = find_timezone("UTC")
        self.assertIsInstance(tz, tzinfo)
        self.assertIsNotNone(tz)
        self.assertEqual(tz, zoneinfo.ZoneInfo("UTC"))

        tz = find_timezone("us/Eastern")
        self.assertIsInstance(tz, tzinfo)
        self.assertIsNotNone(tz)
        self.assertEqual(tz, zoneinfo.ZoneInfo("us/Eastern"))

        tz = find_timezone("foobar")
        self.assertIsNone(tz)

    def test_currenttz(self):
        tz = current_timezone()
        self.assertIsInstance(tz, tzinfo)
        self.assertIsNotNone(tz)
        self.assertEqual(tz, zoneinfo.ZoneInfo(LOCAL_TZ))

    def test_localize(self):
        date = datetime(2020, 10, 15, 20, 15, 13)
        self.assertIsNone(date.tzinfo)

        # makes the date aware
        loc_date = localize_datetime(date)
        self.assertEqual(loc_date.tzinfo.tzname(None), zoneinfo.ZoneInfo(LOCAL_TZ).tzname(None))
        self.assertEqual(date.date(), loc_date.date())
        self.assertEqual(date.time(), loc_date.time())

        # ensures that the aware date can be converted in timezone
        loc_date_2 = localize_datetime(loc_date, "UTC")
        self.assertEqual(loc_date_2.tzinfo.tzname(None), zoneinfo.ZoneInfo("UTC").tzname(None))
        self.assertEqual(date.date(), loc_date_2.date())
        self.assertNotEqual(date.time(), loc_date_2.time())

        # makes sure that conversion back restores original timezone
        loc_date_3 = localize_datetime(loc_date_2, LOCAL_TZ)
        self.assertEqual(loc_date_3.tzinfo.tzname(None), zoneinfo.ZoneInfo(LOCAL_TZ).tzname(None))
        self.assertEqual(loc_date_3.date(), loc_date.date())
        self.assertEqual(loc_date_3.time(), loc_date.time())

        # make sure that timestamp gets changed
        loc_date_4 = localize_datetime(datetime(2021, 10, 21, 5, 44, 18), 'UTC')
        loc_date_5 = localize_datetime(datetime(2021, 10, 21, 5, 44, 18), 'Europe/Berlin')
        self.assertGreater(loc_date_4.timestamp(), loc_date_5.timestamp())
        self.assertEqual(loc_date_4.timestamp(), loc_date_5.timestamp() + (60 * 60 * 2))

    def test_unix(self):
        # pair to check
        unix = 1634394762
        date = datetime(2021, 10, 16, 14, 32, 42, tzinfo=zoneinfo.ZoneInfo("GMT"))

        # run conversion
        conv_date = unix_to_datetime(unix, 'GMT')
        self.assertIsNotNone(conv_date)
        self.assertIsNotNone(conv_date.tzinfo)
        self.assertEqual(conv_date, date)

        # test with string
        date_loc = localize_datetime(date, LOCAL_TZ)
        conv_date = unix_to_datetime(str(unix), LOCAL_TZ)
        self.assertIsNotNone(conv_date)
        self.assertIsNotNone(conv_date.tzinfo)
        self.assertEqual(conv_date, date_loc)

        # test error case
        self.assertRaises(ValueError, unix_to_datetime, "FOO", 'UTC')

    def test_parse(self):
        date_str = "2021-09-15"
        format = "%Y-%m-%d"
        orig_date = datetime(2021, 9, 15, tzinfo=zoneinfo.ZoneInfo("UTC"))

        # test the parsing
        dt = parse_time(date_str, format, "UTC")
        self.assertIsNotNone(dt)
        self.assertEqual(dt, orig_date)
        self.assertEqual(dt.tzinfo.tzname(None), zoneinfo.ZoneInfo("UTC").tzname(None))

        date_str = "2021-09-15_20:14:50"
        format = "%Y-%m-%d_%H:%M:%S"
        orig_date = datetime(2021, 9, 15, 20, 14, 50, tzinfo=zoneinfo.ZoneInfo(LOCAL_TZ))

        # test the parsing
        dt = parse_time(date_str, format, LOCAL_TZ)
        self.assertIsNotNone(dt)
        self.assertEqual(dt, orig_date)
        self.assertEqual(dt.tzinfo.tzname(None), zoneinfo.ZoneInfo(LOCAL_TZ).tzname(None))

        # test error case
        self.assertRaises(ValueError, parse_time, "1020-13-32_12:34:21", format, "UTC")

    def test_aware(self):
        # create basic date
        date = datetime(2020, 10, 15, 20, 15, 13)
        self.assertIsNone(date.tzinfo)

        # ensure that datetime gets added
        loc_date = make_aware(date, 'Europe/Berlin')
        self.assertIsNotNone(loc_date)
        self.assertIsNotNone(loc_date.tzinfo)
        self.assertEqual(date.date(), loc_date.date())
        self.assertEqual(date.time(), loc_date.time())
        self.assertEqual(loc_date.tzinfo.tzname(None), zoneinfo.ZoneInfo("Europe/Berlin").tzname(None))

        # check to make aware timezone aware
        loc_date = make_aware(loc_date, 'Europe/Berlin')
        self.assertIsNotNone(loc_date)
        self.assertIsNotNone(loc_date.tzinfo)
        self.assertEqual(date.date(), loc_date.date())
        self.assertEqual(date.time(), loc_date.time())
        self.assertEqual(loc_date.tzinfo.tzname(None), zoneinfo.ZoneInfo("Europe/Berlin").tzname(None))

        # check switch of timezone
        pre_date = localize_datetime(loc_date, 'Asia/Calcutta')
        loc_date2 = make_aware(loc_date, 'Asia/Calcutta')
        self.assertEqual(pre_date, loc_date2)
        self.assertIsNotNone(loc_date2)
        self.assertIsNotNone(loc_date2.tzinfo)
        self.assertEqual(date.date(), loc_date2.date())
        self.assertEqual((date + timedelta(hours=3, minutes=30)).time(), loc_date2.time())
        self.assertEqual(loc_date2.tzinfo.tzname(None), zoneinfo.ZoneInfo("Asia/Calcutta").tzname(None))

        # make none check
        loc_date = make_aware(None)
        self.assertIsNone(loc_date)

    def test_unaware(self):
        # create data
        date1 = datetime(2021, 1, 1, 15, 10, 30)
        date1_utc = localize_datetime(date1, 'UTC')
        date1_cet = localize_datetime(date1, 'CET')

        self.assertNotEqual(date1_cet.timestamp(), date1_utc.timestamp())

        dt = make_unaware(date1)
        self.assertEqual(dt, date1)

        dt = make_unaware(date1_utc)
        self.assertEqual(dt, date1)

        dt = make_unaware(date1_cet)
        self.assertEqual(dt, date1 - timedelta(hours=1))

        dt = make_unaware(date1_cet, 'UTC')
        self.assertEqual(dt, date1 - timedelta(hours=1))

        dt = make_unaware("2021-07-12")
        self.assertEqual(dt, datetime(2021, 7, 12))

    def test_diff(self):
        # setup the data
        date1 = datetime(2021, 1, 1, 15, 10, 30)
        date2 = datetime(2021, 1, 10, 18, 20, 50)
        orig_diff = timedelta(days=9, hours=3, minutes=10, seconds=20)

        # vanilla test
        diff1 = time_diff(date2, date1)
        self.assertEqual(diff1, orig_diff)
        diff2 = time_diff(date1, date2)
        self.assertEqual(diff2, -orig_diff)

        # localize to first timezone
        date1_utc = localize_datetime(date1, 'UTC')
        diff1 = time_diff(date2, date1_utc, 'UTC')
        self.assertEqual(diff1, orig_diff)
        diff2 = time_diff(date1_utc, date2, 'UTC')
        self.assertEqual(diff2, -orig_diff)

        # localize further should not change inherit time
        date1_cal = localize_datetime(date1_utc, 'Asia/Calcutta')
        diff1 = time_diff(date2, date1_utc, 'UTC')
        self.assertEqual(diff1, orig_diff)

        # test different timezones (times are then compared in utc, so diff should remove 1 hour)
        date2_cet = localize_datetime(date2, 'Europe/Berlin')
        diff1 = time_diff(date2_cet, date1_utc)
        self.assertEqual(diff1, orig_diff - timedelta(hours=1))

        # convert the other timezone
        date1_cal = localize_datetime(date1, 'Asia/Calcutta')
        diff1 = time_diff(date2_cet, date1_cal)
        self.assertEqual(diff1, orig_diff + timedelta(hours=4, minutes=30))

    def test_pandas_timezone(self):
        df = pd.DataFrame(
            [
                [
                    pd.Timestamp("2020-06-06").tz_localize("Europe/Berlin"),
                    "foo",
                ],
                [
                    pd.Timestamp("2020-06-06").tz_localize("Europe/Berlin"),
                    "bar"
                ]
            ],
            columns=["date", "text"]
        )

        # check error cases
        self.assertRaises(ValueError, has_timezone_pandas, None, None)
        self.assertRaises(ValueError, has_timezone_pandas, df, None)
        self.assertRaises(ValueError, has_timezone_pandas, df, "no_col")
        self.assertRaises(ValueError, has_timezone_pandas, df, "text")

        # check datetime cases
        val = has_timezone_pandas(df, "date")
        self.assertTrue(val)

        # update dataframej
        df = pd.DataFrame(
            [
                [
                    pd.Timestamp("2020-06-06"),
                    "foo",
                ],
                [
                    pd.Timestamp("2020-06-06"),
                    "bar"
                ]
            ],
            columns=["date", "text"]
        )
        val = has_timezone_pandas(df, "date")
        self.assertFalse(val)

    def test_pandas_aware(self):
        df = pd.DataFrame(
            [
                [
                    pd.Timestamp("2020-06-06"),
                    "foo",
                ],
                [
                    pd.Timestamp("2020-06-06"),
                    "bar"
                ]
            ],
            columns=["date", "text"]
        )

        # check error cases
        val = make_aware_pandas(None, None)
        self.assertIsNone(val)
        self.assertRaises(ValueError, make_aware_pandas, df, None)
        self.assertRaises(RuntimeError, make_aware_pandas, df, "no_col")

        df_new = make_aware_pandas(df, "date")
        self.assertTrue(has_timezone_pandas(df_new, "date"))

        df = pd.DataFrame(
            [
                [
                    "2020-06-06",
                    "foo",
                ],
                [
                    "2020-06-06",
                    "bar"
                ]
            ],
            columns=["date", "text"]
        )
        df_new = make_aware_pandas(df, "date")
        self.assertTrue(has_timezone_pandas(df_new, "date"))

        # TODO: add additional test cases here

    def test_convert_datetime(self):
        '''Tests various use cases for the convert datetime functions.'''
        # TODO: integrate tests for time, date, and datetime conversions
        pass

    def test_time_to_interval(self):
        '''Tests if the conversion is correct'''
        dt = datetime(2020, 9, 23, 12, 00)
        iv = time_to_interval(dt, 0)
        self.assertEqual(iv, 0)

        iv = time_to_interval(dt, 0, zero_center=False, normalize=True)
        self.assertEqual(iv, .5)

        iv = time_to_interval(dt, 12)
        self.assertEqual(iv, 0)

        iv = time_to_interval(dt, 12, zero_center=False, normalize=True)
        self.assertEqual(iv, .5)

        iv = time_to_interval(dt, 12, zero_center=False, normalize=False)
        self.assertEqual(iv, 24 * 60)

        # test time after the day
        dt = datetime(2020, 9, 24, 6, 00)
        base = dt - timedelta(hours=12)
        self.assertEqual(base.day, 23)

        iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=True)
        self.assertEqual(iv, 42 / 48)

        iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=False)
        self.assertEqual(iv, 42 * 60)

        iv = time_to_interval(dt, 12, baseline=base, zero_center=True, normalize=True)
        self.assertEqual(iv, 18 / 48)

        # test time before the day
        dt = datetime(2020, 9, 22, 22, 00)
        base = dt + timedelta(hours=12)
        self.assertEqual(base.day, 23)

        iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=True)
        self.assertEqual(iv, 10 / 48)

        iv = time_to_interval(dt, 12, baseline=base, zero_center=False, normalize=False)
        self.assertEqual(iv, 10 * 60)

        iv = time_to_interval(dt, 12, baseline=base, zero_center=True, normalize=True)
        self.assertEqual(iv, -14 / 48)

        # test async offset
        dt = datetime(2020, 9, 24, 6, 00)
        base = dt - timedelta(hours=12)
        self.assertEqual(base.day, 23)

        iv = time_to_interval(dt, (6, 12), baseline=base, zero_center=False, normalize=True)
        self.assertEqual(iv, 36 / 42)

        iv = time_to_interval(dt, (12, 6), baseline=base, zero_center=False, normalize=False)
        self.assertEqual(iv, 42 * 60)

        iv = time_to_interval(dt, (6, 12), baseline=base, zero_center=False, normalize=False)
        self.assertEqual(iv, 36 * 60)

        iv = time_to_interval(dt, (6, 12), baseline=base, zero_center=True, normalize=True)
        self.assertEqual(iv, 15 / 42)
