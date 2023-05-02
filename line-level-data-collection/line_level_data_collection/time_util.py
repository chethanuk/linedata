import datetime as dt

from dateutil.parser import parse


def utc_datetime_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_timestamp_iso_string_utc(timestamp_str) -> dt.datetime:
    # more robust parsing of time
    return parse(timestamp_str).astimezone(dt.timezone.utc)


def utc_timestamp_to_iso_string(ts: dt.datetime) -> str:
    return ts.isoformat()
