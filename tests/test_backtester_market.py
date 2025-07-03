import numpy as np
import pytest
from ccxt.base.errors import BadSymbol

from .utils import assert_timestamps_in_range


@pytest.fixture
def expected_sol_ticker():
    return {
        "symbol": "SOL/USDT",
        "timestamp": 1735687800000,
        "datetime": "2024-12-31 23:30:00",
        "high": 190.5,
        "low": 190.38,
        "open": 190.45,
        "baseVolume": 1394.013,
        "last": 190.49,
        "close": 190.49,
        "previousClose": 190.46,
        "change": 0.04,
        "percentage": 0.021,
        "average": 190.47,
    }


@pytest.fixture
def expected_test_ticker():
    return {
        "symbol": "TEST/PAIR",
        "timestamp": 1735687800000,
        "datetime": "2024-12-31 23:30:00",
        "high": 190.5,
        "low": 190.38,
        "open": 190.45,
        "baseVolume": 1394.013,
        "last": 190.49,
        "close": 190.49,
        "previousClose": 190.46,
        "change": 0.04,
        "percentage": 0.021,
        "average": 190.47,
    }


@pytest.fixture
def expected_btc_ticker():
    return {
        "symbol": "BTC/USDT",
        "timestamp": 1735687800000,
        "datetime": "2024-12-31 23:30:00",
        "high": 93731.06,
        "low": 93725.67,
        "open": 93725.68,
        "baseVolume": 2.28303,
        "last": 93731.05,
        "close": 93731.05,
        "previousClose": 93725.68,
        "change": 5.37,
        "percentage": 0.006,
        "average": 93728.36499999999,
    }


def test_backtester_raises_error_when_adding_existing_data_feed(
    backtester_with_data_feed,
):
    with pytest.raises(NameError):
        backtester_with_data_feed.add_data_feed(
            "SOL/USDT", "1m", "./data/test-sol-data.json"
        )


def test_backtester_fetch_ticker(backtester_with_data_feed, expected_btc_ticker):
    sol_ticker = backtester_with_data_feed.fetch_ticker("BTC/USDT")
    expected_result = expected_btc_ticker
    assert sol_ticker == expected_result


def test_backtester_fetch_tickers(
    backtester_with_data_feed,
    expected_sol_ticker,
    expected_btc_ticker,
    expected_test_ticker,
):
    tickers = backtester_with_data_feed.fetch_tickers()
    expected_result = [expected_sol_ticker, expected_btc_ticker, expected_test_ticker]

    assert tickers == expected_result


def test_backtester_fetch_ticker_with_invalid_symbol(backtester_with_data_feed):
    with pytest.raises(BadSymbol):
        backtester_with_data_feed.fetch_ticker("INVALID/USDT")


def test_get_ohlcv_on_base_timeframe(backtester_with_data_feed):
    ohlcv = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "1m")
    assert ohlcv.shape == (60, 6)


def test_get_ohlcv_on_higher_timeframe_works(backtester_with_data_feed):
    ohlcv = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "15m")
    expected_ohlcv = [
        [1735686000000, 93488.83, 93756.0, 93375.38, 93712.56, 117.78087],
        [1735686900000, 93712.57, 93753.47, 93602.83, 93731.05, 58.09506],
        [1735687800000, 93731.06, 93734.91, 93456.0, 93490.87, 99.67114],
        [1735688700000, 93490.86, 93702.15, 93484.3, 93576.0, 61.03288],
    ]  # 15m candle fetched from binance
    assert np.allclose(expected_ohlcv, ohlcv, atol=1e-12)


def test_get_ohlcv_on_non_traditional_timeframe_works(backtester_with_data_feed):
    ohlcv = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "6m")
    assert ohlcv.shape == (10, 6)


def test_get_ohlcv_multiple_times_do_not_conflict(backtester_with_data_feed):
    ohlcv1 = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "5m")
    ohlcv2 = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "1m")
    ohlcv3 = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "30m")
    ohlcv4 = backtester_with_data_feed.fetch_ohlcv("SOL/USDT", "15m")

    assert ohlcv1.shape == (12, 6)
    assert ohlcv2.shape == (60, 6)
    assert ohlcv3.shape == (2, 6)
    assert ohlcv4.shape == (4, 6)


def test_get_ohlcv_with_start_time(backtester_with_data_feed):
    ohlcv = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "5m", since=1735687800000)
    assert ohlcv.shape == (6, 6)
    first_expected_timestamp = 1735687800000
    last_expected_timestamp = 1735689300000
    assert_timestamps_in_range(ohlcv, first_expected_timestamp, last_expected_timestamp)


def test_get_ohlcv_with_end_time(backtester_with_data_feed):
    ohlcv = backtester_with_data_feed.fetch_ohlcv(
        "BTC/USDT", "5m", params={"until": 1735687800000}
    )
    assert ohlcv.shape == (6, 6)
    first_expected_timestamp = 1735686000000
    last_expected_timestamp = 1735687500000
    assert_timestamps_in_range(ohlcv, first_expected_timestamp, last_expected_timestamp)


def test_get_ohlcv_with_valid_irregular_start_time(backtester_with_data_feed):
    ohlcv = backtester_with_data_feed.fetch_ohlcv("BTC/USDT", "5m", since=1735687680000)
    assert ohlcv.shape == (6, 6)
    first_expected_timestamp = 1735687800000
    last_expected_timestamp = 1735689300000
    assert_timestamps_in_range(ohlcv, first_expected_timestamp, last_expected_timestamp)


def test_get_ohlcv_on_invalid_pair(backtester_with_data_feed):
    with pytest.raises(BadSymbol):
        backtester_with_data_feed.fetch_ohlcv("INVALID/USDT", "5m")
