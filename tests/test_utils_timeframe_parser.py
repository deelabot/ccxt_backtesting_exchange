import pytest
from datetime import timedelta
from ccxt_backtesting_exchange.utils import timeframe_to_timedelta


def test_timeframe_to_timedelta_seconds():
    assert timeframe_to_timedelta("30s") == timedelta(seconds=30)


def test_timeframe_to_timedelta_minutes():
    assert timeframe_to_timedelta("15m") == timedelta(minutes=15)


def test_timeframe_to_timedelta_hours():
    assert timeframe_to_timedelta("4h") == timedelta(hours=4)


def test_timeframe_to_timedelta_days():
    assert timeframe_to_timedelta("1d") == timedelta(days=1)


def test_timeframe_to_timedelta_weeks():
    assert timeframe_to_timedelta("1w") == timedelta(weeks=1)


def test_timeframe_to_timedelta_invalid_format():
    with pytest.raises(ValueError, match="Invalid timeframe format: 10xx"):
        timeframe_to_timedelta("10xx")


def test_timeframe_to_timedelta_unsupported_unit():
    with pytest.raises(ValueError, match="Unsupported unit in timeframe: M"):
        timeframe_to_timedelta("1M")
