import pytest
import numpy as np
from ccxt_backtesting_exchange.data_feed import DataFeed


@pytest.fixture
def data_feed():
    return DataFeed("./data/test-data.json")


@pytest.fixture()
def empty_data_feed():
    return DataFeed("./data/empty.json")


def test_get_data_between_timestamps(data_feed):
    data = data_feed.get_data_between_timestamps()
    assert len(data) == 60
    assert isinstance(data, np.ndarray)


def test_empty_data_feed(empty_data_feed):
    data = empty_data_feed.get_data_between_timestamps()
    assert len(data) == 0


def test_get_data_between_timestamps_with_valid_range(data_feed):
    start = 1735686600000
    end = 1735688400000
    data = data_feed.get_data_between_timestamps(start=start, end=end)
    assert len(data) == 30

    # Ensure all timestamps are within the specified range
    assert np.all(data[:, 0] >= start)
    assert np.all(data[:, 0] < end)


def test_get_data_between_timestamps_with_valid_range_and_limit(data_feed):
    start = 1735686600000
    end = 1735688400000
    limit = 10
    data = data_feed.get_data_between_timestamps(start=start, end=end, limit=limit)
    assert len(data) == 10

    # Ensure all timestamps are within the specified range
    assert np.all(data[:, 0] >= start)
    assert np.all(data[:, 0] < end)


def test_get_data_between_timestamps_with_start(data_feed):
    start = 1735686600000
    data = data_feed.get_data_between_timestamps(start=start)
    assert len(data) == 50
    assert np.all(data[:, 0] >= start)


def test_get_data_between_timestamps_with_end(data_feed):
    end = 1735688400000
    data = data_feed.get_data_between_timestamps(end=end)
    assert len(data) == 40
    assert np.all(data[:, 0] < end)
