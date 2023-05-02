import datetime as dt

from dateutil.tz import tzutc

from dateutil.tz import gettz

from line_level_data_collection.time_util import utc_datetime_now, parse_timestamp_iso_string_utc, \
    utc_timestamp_to_iso_string


def test_utc_now():
    ts = utc_datetime_now()
    assert ts.tzinfo == dt.timezone.utc


def test_datetime_equivalence():
    assert dt.datetime(year=2000, day=10, month=10, tzinfo=tzutc()) == dt.datetime(year=2000, day=10, month=10,
                                                                                   tzinfo=dt.timezone.utc)


def test_parse_iso_string_to_utc():
    expected = dt.datetime(tzinfo=dt.timezone.utc, year=2021, month=8, day=20,
                           hour=18, minute=36, second=19,
                           microsecond=595 * 1000)
    dt1 = parse_timestamp_iso_string_utc("2021-08-20T19:36:19.595+01:00")
    assert dt1 == expected
    assert dt1.tzinfo == dt.timezone.utc
    dt2 = parse_timestamp_iso_string_utc("2021-08-20T18:36:19.595Z")
    assert dt2 == expected
    assert dt2.tzinfo == dt.timezone.utc


def test_timestamp_round_trip():
    # str to str
    assert utc_timestamp_to_iso_string(
        parse_timestamp_iso_string_utc("2021-08-20T19:36:19.595+01:00")) == "2021-08-20T18:36:19.595000+00:00"
    assert utc_timestamp_to_iso_string(
        parse_timestamp_iso_string_utc("2021-08-20T18:36:19.595+00:00")) == "2021-08-20T18:36:19.595000+00:00"

    # datetime to datetime
    ts = dt.datetime(tzinfo=dt.timezone.utc, year=2021, month=8, day=20,
                     hour=18, minute=36, second=19,
                     microsecond=595 * 1000)
    assert parse_timestamp_iso_string_utc(utc_timestamp_to_iso_string(ts)) == ts
    ts_hk = dt.datetime(tzinfo=gettz('Asia/Hong_Kong'), year=2021, month=8, day=21,
                        hour=2, minute=36, second=19,
                        microsecond=595 * 1000)
    result = parse_timestamp_iso_string_utc(utc_timestamp_to_iso_string(ts_hk))
    assert result.tzinfo == dt.timezone.utc
    assert result == ts
