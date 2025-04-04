from datetime import datetime, timezone

import pytz

from utils.common.datatime import (
    fromtimestamp,
    now,
    to_utc,
    utc_to_timezone_return_naive,
    utcnow,
    utcnow_to_timezone_return_naive,
)


def test_now():
    dt = now()
    assert dt.tzinfo is not None


def test_utcnow():
    dt = utcnow()
    assert dt.tzinfo == timezone.utc


def test_to_utc():
    # Test naive datetime
    naive_dt = datetime(2024, 1, 1, 12, 0)
    utc_dt = to_utc(naive_dt)
    assert utc_dt.tzinfo == timezone.utc

    # Test aware datetime
    ny_tz = pytz.timezone('America/New_York')
    aware_dt = datetime(2024, 1, 1, 12, 0, tzinfo=ny_tz)
    utc_dt = to_utc(aware_dt)
    assert utc_dt.tzinfo == timezone.utc


def test_fromtimestamp():
    timestamp = 1704067200  # 2024-01-01 00:00:00 UTC
    dt = fromtimestamp(timestamp)
    assert dt.tzinfo == timezone.utc
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 1


def test_utc_to_timezone_return_naive():
    utc_dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    ny_naive = utc_to_timezone_return_naive(utc_dt, 'America/New_York')
    assert ny_naive.tzinfo is None


def test_utcnow_to_timezone_return_naive():
    naive_dt = utcnow_to_timezone_return_naive('America/New_York')
    assert naive_dt.tzinfo is None 