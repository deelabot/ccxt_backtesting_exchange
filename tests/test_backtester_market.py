import pytest


@pytest.fixture
def backtester_with_data_feed(backtester):
    backtester.add_data_feed("SOL/USDT", "1m", "./data/test-sol-data.json")
    backtester.add_data_feed("BTC/USDT", "1m", "./data/test-btc-data.json")

    return backtester


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


def test_backtester_fetch_ticker(backtester_with_data_feed, expected_btc_ticker):
    sol_ticker = backtester_with_data_feed.fetch_ticker("BTC/USDT")
    expected_result = expected_btc_ticker
    assert sol_ticker == expected_result


def test_backtester_fetch_tickers(
    backtester_with_data_feed, expected_sol_ticker, expected_btc_ticker
):
    tickers = backtester_with_data_feed.fetch_tickers()
    expected_result = [expected_sol_ticker, expected_btc_ticker]
    assert tickers == expected_result
