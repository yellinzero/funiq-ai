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


def get_time_in_timezone(tz: str = 'Asia/Shanghai') -> datetime.time:
    """Get current time (without date) in specified timezone."""
    return utcnow_to_timezone_return_naive(tz).time()


def get_date_in_timezone(tz: str = 'Asia/Shanghai') -> datetime.date:
    """Get current date in specified timezone."""
    return utcnow_to_timezone_return_naive(tz).date()


def format_datetime(dt: datetime.datetime, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime to string with given format."""
    return dt.strftime(format)


def parse_datetime(dt_str: str, format: str = '%Y-%m-%d %H:%M:%S') -> datetime.datetime:
    """Parse datetime string with given format."""
    return datetime.datetime.strptime(dt_str, format)


def is_same_day(dt1: datetime.datetime, dt2: datetime.datetime, tz: str = 'Asia/Shanghai') -> bool:
    """Check if two datetimes are in the same day in specified timezone."""
    dt1_tz = utc_to_timezone_return_naive(dt1, tz)
    dt2_tz = utc_to_timezone_return_naive(dt2, tz)
    return dt1_tz.date() == dt2_tz.date()


def get_day_start_end(tz: str = 'Asia/Shanghai') -> tuple[datetime.datetime, datetime.datetime]:
    """Get start and end of current day in specified timezone."""
    current = utcnow_to_timezone_return_naive(tz)
    start = current.replace(hour=0, minute=0, second=0, microsecond=0)
    end = current.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def add_days(dt: datetime.datetime, days: int) -> datetime.datetime:
    """Add or subtract days from datetime."""
    return dt + datetime.timedelta(days=days)


def add_hours(dt: datetime.datetime, hours: int) -> datetime.datetime:
    """Add or subtract hours from datetime."""
    return dt + datetime.timedelta(hours=hours)


def get_seconds_until(target_time: datetime.time, tz: str = 'Asia/Shanghai') -> int:
    """Get seconds until next occurrence of target_time in specified timezone."""
    now = utcnow_to_timezone_return_naive(tz)
    target = now.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=0
    )
    if target <= now:
        target = add_days(target, 1)
    return int((target - now).total_seconds())


def is_before(time1: datetime.time, time2: datetime.time) -> bool:
    """Check if time1 is before time2."""
    return time1 < time2


def is_after(time1: datetime.time, time2: datetime.time) -> bool:
    """Check if time1 is after time2."""
    return time1 > time2


def is_between(
    time: datetime.time, 
    start: datetime.time, 
    end: datetime.time,
    inclusive: bool = True
) -> bool:
    """
    Check if time is between start and end.
    For normal range (e.g. 10:00-14:00): start <= time <= end
    For cross-day range (e.g. 22:00-02:00): time >= start or time <= end
    """
    if inclusive:
        return (start <= time <= end) if start <= end else (time >= start or time <= end)
    else:
        return (start < time < end) if start <= end else (time > start or time < end)


def is_between_hours(
    time: datetime.time,
    start_hour: int,
    end_hour: int,
    inclusive: bool = True
) -> bool:
    """Check if time is between start_hour and end_hour."""
    start = datetime.time(start_hour)
    end = datetime.time(end_hour)
    return is_between(time, start, end, inclusive)


def compare_times_in_timezone(
    dt1: datetime.datetime,
    dt2: datetime.datetime,
    tz: str = 'Asia/Shanghai'
) -> int:
    """
    Compare two datetimes in specified timezone.
    Returns:
        -1 if dt1 < dt2
         0 if dt1 == dt2
         1 if dt1 > dt2
    """
    dt1_tz = utc_to_timezone_return_naive(dt1, tz)
    dt2_tz = utc_to_timezone_return_naive(dt2, tz)
    return -1 if dt1_tz < dt2_tz else 1 if dt1_tz > dt2_tz else 0
