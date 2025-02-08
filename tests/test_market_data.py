from datetime import datetime, timedelta, timezone
import json
import os

import pandas as pd
import pytest


from ccxt_backtesting_exchange.market_data import MarketDataCache
from .utils import assert_timestamps_in_range


@pytest.fixture
def market_data_cache():
    cache = MarketDataCache(exchange_id="binance", symbol="TEST/PAIR", timeframe="1m")
    yield cache

    if os.path.exists(cache.file_path):
        os.remove(cache.file_path)


@pytest.fixture
def df():
    with open("./data/test-sol-data.json", "r") as file:
        data = json.load(file)
    df = pd.DataFrame(
        data, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = df["timestamp"].astype("int64")
    df.iloc[:, 1:] = df.iloc[:, 1:].astype("float64")
    return df


def test_initialization(market_data_cache):
    assert market_data_cache.exchange.id == "binance"
    assert market_data_cache.symbol == "TEST/PAIR"
    assert market_data_cache.timeframe == "1m"
    assert market_data_cache.interval == timedelta(minutes=1)
    assert market_data_cache.file_path == "./data/test_pair_1m.json"


def test_initialization_with_invalid_exchange():
    with pytest.raises(ValueError, match="Exchange invalid not supported by ccxt."):
        MarketDataCache(exchange_id="invalid", symbol="TEST/PAIR", timeframe="1m")


def test_convert_to_dataframe(market_data_cache):
    ohlcv = [
        [1609459200000, 29000.0, 29500.0, 28500.0, 29200.0, 100.0],
        [1609459260000, 29200.0, 29300.0, 29100.0, 29250.0, 50.0],
    ]
    df = market_data_cache._MarketDataCache__convert_to_dataframe(ohlcv)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 6)
    assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]


def test_split_gap_into_chunks(market_data_cache):
    gaps = [(datetime(2021, 1, 1), datetime(2021, 1, 2))]
    max_delta = timedelta(hours=1)
    chunks = market_data_cache.split_gap_into_chunks(gaps, max_delta)
    assert len(chunks) == 24
    assert chunks[0] == (datetime(2021, 1, 1), datetime(2021, 1, 1, 1))
    assert chunks[-1] == (datetime(2021, 1, 1, 23), datetime(2021, 1, 2))


def test_identify_data_gaps_on_empty_df(market_data_cache):
    df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    start_time = datetime(2021, 1, 1)
    end_time = datetime(2021, 1, 2)
    gaps = market_data_cache.identify_data_gaps(df, start_time, end_time)
    assert len(gaps) == 1
    assert gaps[0] == (start_time, end_time)


def test_identify_data_gaps_on_non_empty(market_data_cache):
    df = pd.DataFrame(
        {
            "timestamp": [1609459200000, 1609459260000],
            "open": [29000.0, 29200.0],
            "high": [29500.0, 29300.0],
            "low": [28500.0, 29100.0],
            "close": [29200.0, 29250.0],
            "volume": [100.0, 50.0],
        }
    )
    start_time = datetime(2021, 1, 1)
    end_time = datetime(2021, 1, 2)
    gaps = market_data_cache.identify_data_gaps(df, start_time, end_time)
    assert len(gaps) > 0


def test_identify_data_gaps_on_full_data(market_data_cache, df):

    start_time = datetime(2024, 12, 31, 23, tzinfo=timezone.utc)
    end_time = datetime(2024, 12, 31, 23, 30, tzinfo=timezone.utc)
    gaps = market_data_cache.identify_data_gaps(df, start_time, end_time)
    assert len(gaps) == 0


def test_identify_data_gaps_on_data_with_multiple_gaps(market_data_cache, df):

    # Drop some rows to create gaps
    df = df.drop(df.index[11:15])
    df = df.drop(df.index[5:8])

    start_time = datetime(2024, 12, 31, 23, tzinfo=timezone.utc)
    end_time = datetime(2024, 12, 31, 23, 30, tzinfo=timezone.utc)
    gaps = market_data_cache.identify_data_gaps(df, start_time, end_time)
    assert len(gaps) == 2

    assert gaps[0] == (
        datetime(2024, 12, 31, 23, 5, tzinfo=timezone.utc),
        datetime(2024, 12, 31, 23, 8, tzinfo=timezone.utc),
    )

    assert gaps[1] == (
        datetime(2024, 12, 31, 23, 11, tzinfo=timezone.utc),
        datetime(2024, 12, 31, 23, 15, tzinfo=timezone.utc),
    )


def test_save_data(market_data_cache, df):
    # duplicate some rows
    df = pd.concat([df, df.iloc[5:10]])
    df = pd.concat([df, df.iloc[20:30]])

    # shuffle the rows
    df = df.sample(frac=1).reset_index(drop=True)
    assert df.shape == (75, 6)

    market_data_cache.save_data(df)
    # check if the data is saved correctly

    df = market_data_cache.load_existing_data()
    assert df.shape == (60, 6)  # assert that the duplicates are removed
    assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]

    # assert the content of two files are the same
    with open("./data/test_pair_1m.json", "r") as file:
        saved_data = json.load(file)

    with open("./data/test-sol-data.json", "r") as file:
        original_data = json.load(file)

    assert saved_data == original_data


def test_sync_with_backtester(market_data_cache, backtester_with_data_feed):

    market_data_cache.exchange = backtester_with_data_feed
    market_data_cache.sync(
        datetime(2024, 12, 31, 23, tzinfo=timezone.utc),
        datetime(2024, 12, 31, 23, 30, tzinfo=timezone.utc),
        chunk_size=100,
    )
    assert os.path.exists(market_data_cache.file_path)
    df = market_data_cache.load_existing_data()
    assert df.shape == (30, 6)
    assert_timestamps_in_range(df.to_numpy(), 1735686000000, 1735687740000)
