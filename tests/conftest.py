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


@pytest.fixture
def backtester_with_data_feed(backtester):
    backtester.add_data_feed("SOL/USDT", "1m", "./data/test-sol-data.json")
    backtester.add_data_feed("BTC/USDT", "1m", "./data/test-btc-data.json")
    backtester.add_data_feed("TEST/PAIR", "1m", "./data/test-sol-data.json")

    return backtester


@pytest.fixture
def backtest_with_data_feed_and_orders(backtester_with_data_feed):
    backtester_with_data_feed.create_order("SOL/USDT", "limit", "buy", 1.0, 190.30)
    backtester_with_data_feed.create_order("SOL/USDT", "limit", "buy", 1.0, 190.25)
    backtester_with_data_feed.create_order("SOL/USDT", "market", "buy", 1.0, 190.49)
    backtester_with_data_feed.create_order("SOL/USDT", "market", "sell", 1.0, 190.49)

    return backtester_with_data_feed
