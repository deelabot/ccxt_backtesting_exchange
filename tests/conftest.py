from datetime import datetime, timedelta, timezone

import pytest


from ccxt_backtesting_exchange.backtester import Backtester
from ccxt_backtesting_exchange.clock import Clock


@pytest.fixture
def clock():
    clock = Clock(
        start_time=datetime(
            month=12, day=31, year=2024, hour=23, minute=30, tzinfo=timezone.utc
        ),
        end_time=datetime(
            month=12,
            day=31,
            year=2024,
            hour=23,
            minute=59,
            tzinfo=timezone.utc,
        ),
        interval=timedelta(minutes=1),
    )
    return clock


@pytest.fixture
def backtester(clock):
    return Backtester(
        balances={"BTC": 1.0, "ETH": 5.0, "SOL": 10.0, "USDT": 10000.0},
        clock=clock,
        fee=0.001,
    )
