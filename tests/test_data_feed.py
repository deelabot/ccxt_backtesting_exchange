import pytest
import numpy as np
from ccxt_backtesting_exchange.data_feed import DataFeed


@pytest.fixture
def data_feed():
    return DataFeed("./data/test-data.json")


@pytest.fixture()
def empty_data_feed():
    return DataFeed("./data/empty.json")


def assert_timestamps_in_range(
    data: np.ndarray,
    first_expected_timestamp: np.float32,
    last_expected_timestamp: np.float32,
):
    """
    Assert that all timestamps in the data are within the specified range.

    :param data: A NumPy array or list of timestamps.
    :param first_expected_timestamp: The first timestamp returned.
    :param last_expected_timestamp: The last allowable timestamp.
    """
    assert isinstance(data, np.ndarray), "Data must be a NumPy array"
    assert len(data) > 0, "Data should not be empty"

    returned_timestamps = data[:, 0]
    first_returned_timestamp = returned_timestamps[0]
    last_returned_timestamp = returned_timestamps[-1]

    assert first_returned_timestamp == first_expected_timestamp
    assert last_returned_timestamp == last_expected_timestamp
    assert np.all(returned_timestamps >= first_expected_timestamp)
    assert np.all(returned_timestamps <= last_expected_timestamp)


def test_get_data_between_timestamps(data_feed):
    data = data_feed.get_data_between_timestamps()
    first_expected_timestamp = 1735686000000
    last_expected_timestamp = 1735689540000
    assert len(data) == 60
    assert_timestamps_in_range(data, first_expected_timestamp, last_expected_timestamp)


def test_empty_data_feed(empty_data_feed):
    data = empty_data_feed.get_data_between_timestamps()
    assert len(data) == 0


def test_get_data_between_timestamps_with_valid_range(data_feed):
    start = 1735686600000
    end = 1735688400000
    data = data_feed.get_data_between_timestamps(start=start, end=end)
    last_expected_timestamp = 1735688340000
    assert len(data) == 30
    assert_timestamps_in_range(
        data,
        start,
        last_expected_timestamp,
    )


def test_get_data_between_timestamps_with_limit(data_feed):
    start = 1735686600000
    end = 1735688400000
    limit = 10
    data = data_feed.get_data_between_timestamps(start=start, end=end, limit=limit)
    first_expected_timestamp = 1735687800000
    last_expected_timestamp = 1735688340000
    assert len(data) == 10

    assert_timestamps_in_range(
        data,
        first_expected_timestamp,
        last_expected_timestamp,
    )


def test_get_data_from_timestamp_with_limit(data_feed):
    start = 1735686600000
    limit = 10
    data = data_feed.get_data_between_timestamps(start=start, limit=limit)
    first_expected_timestamp = 1735686600000
    last_expected_timestamp = 1735687140000
    assert len(data) == 10

    assert_timestamps_in_range(
        data,
        first_expected_timestamp,
        last_expected_timestamp,
    )


def test_get_data_upto_timestamp_with_limit(data_feed):
    end = 1735688400000
    limit = 10
    data = data_feed.get_data_between_timestamps(end=end, limit=limit)
    first_expected_timestamp = 1735687800000
    last_expected_timestamp = 1735688340000
    assert len(data) == 10

    assert_timestamps_in_range(
        data,
        first_expected_timestamp,
        last_expected_timestamp,
    )


def test_get_data_between_timestamps_with_start(data_feed):
    start = 1735686600000
    data = data_feed.get_data_between_timestamps(start=start)
    assert len(data) == 50
    last_expected_timestamp = 1735689540000
    assert_timestamps_in_range(data, start, last_expected_timestamp)


def test_get_data_between_timestamps_with_end(data_feed):
    end = 1735688400000
    data = data_feed.get_data_between_timestamps(end=end)
    first_expected_timestamp = 1735686000000
    last_expected_timestamp = 1735688340000
    assert len(data) == 40
    assert_timestamps_in_range(data, first_expected_timestamp, last_expected_timestamp)


def test_get_data_at_timestamp(data_feed):
    timestamp = 1735686600000
    data = data_feed._get_data_at_timestamp(timestamp)
    assert data[0] == timestamp


def test_get_data_at_timestamp_with_positive_offset(data_feed):
    timestamp = 1735686600000
    offset = 10

    data = data_feed._get_data_at_timestamp(timestamp, offset)
    expected_timestamp = 1735687200000
    assert data[0] == expected_timestamp


def test_get_data_at_timestamp_with_negative_offset(data_feed):
    timestamp = 1735687200000
    offset = -10

    data = data_feed._get_data_at_timestamp(timestamp, offset)
    expected_timestamp = 1735686600000
    assert data[0] == expected_timestamp


def test_get_data_at_timestamp_with_out_of_bounds_offset(data_feed):
    timestamp = 1735686600000
    offset = 100
    with pytest.raises(IndexError):
        data_feed._get_data_at_timestamp(timestamp, offset)


def test_get_data_at_timestamp_with_empty_data_feed(empty_data_feed):
    timestamp = 1735686600000
    data = empty_data_feed._get_data_at_timestamp(timestamp)
    assert len(data) == 0
    assert isinstance(data, np.ndarray)
