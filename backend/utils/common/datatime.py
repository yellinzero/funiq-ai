import datetime

import pytz

_tz_utc = datetime.timezone.utc


def now() -> datetime.datetime:
    """Get the current datetime in the local timezone. Returns a timezone-aware datetime object."""
    return datetime.datetime.now().astimezone()


def utcnow() -> datetime.datetime:
    """Get the current datetime in UTC. Returns a timezone-aware datetime object."""
    return datetime.datetime.now(tz=_tz_utc)


def to_utc(v: datetime.datetime) -> datetime.datetime:
    """Convert a datetime object to UTC. If the object is timezone-naive, it is assumed to be in UTC."""
    if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
        v = v.replace(tzinfo=_tz_utc)
    return v.astimezone(_tz_utc)


def fromtimestamp(timestamp: int | float, tz=_tz_utc) -> datetime.datetime:
    """Convert a timestamp to a datetime object in the given timezone(defaults to UTC)."""
    if tz is None:
        tz = _tz_utc
    return datetime.datetime.fromtimestamp(timestamp, tz=tz)


def utc_to_timezone_return_naive(dt_utc: datetime.datetime, tz: str) -> datetime.datetime:
    dt_target_tz = dt_utc.astimezone(pytz.timezone(tz))
    return dt_target_tz.replace(tzinfo=None)


def utcnow_to_timezone_return_naive(tz: str) -> datetime.datetime:
    dt_utc = utcnow()
    return utc_to_timezone_return_naive(dt_utc, tz)
