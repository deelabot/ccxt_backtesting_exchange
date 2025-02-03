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


def test_get_data_without_limit_returns_all(data_feed):
    data = data_feed.get_data_between_timestamps()
    first_expected_timestamp = 1735686000000
    last_expected_timestamp = 1735689540000
    assert len(data) == 60
    assert_timestamps_in_range(data, first_expected_timestamp, last_expected_timestamp)


def test_get_data_with_limit_returns_most_recent(data_feed):
    data = data_feed.get_data_between_timestamps(limit=10)
    first_expected_timestamp = 1735689000000
    last_expected_timestamp = 1735689540000
    assert len(data) == 10
    assert_timestamps_in_range(data, first_expected_timestamp, last_expected_timestamp)


def test_empty_data_feed_returns_empty(empty_data_feed):
    data = empty_data_feed.get_data_between_timestamps()
    assert len(data) == 0


def test_get_data_between_timestamps_with_valid_range_returns_all(data_feed):
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


def test_get_data_between_timestamps_with_limit_returns_most_recent(data_feed):
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


def test_get_data_from_timestamp_with_limit_returns_earliest(data_feed):
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


def test_get_data_upto_timestamp_with_limit_returns_most_recent(data_feed):
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


def test_get_data_upto_timestamps_with_end(data_feed):
    end = 1735688400000
    data = data_feed.get_data_between_timestamps(end=end)
    first_expected_timestamp = 1735686000000
    last_expected_timestamp = 1735688340000
    assert len(data) == 40
    assert_timestamps_in_range(data, first_expected_timestamp, last_expected_timestamp)


def test_get_data_at_timestamp(data_feed):
    timestamp = 1735686600000
    data = data_feed.get_data_at_timestamp(timestamp)
    assert data[0] == timestamp


def test_get_data_at_timestamp_with_positive_offset(data_feed):
    timestamp = 1735686600000
    offset = 10

    data = data_feed.get_data_at_timestamp(timestamp, offset)
    expected_timestamp = 1735687200000
    assert data[0] == expected_timestamp


def test_get_data_at_timestamp_with_negative_offset(data_feed):
    timestamp = 1735687200000
    offset = -10

    data = data_feed.get_data_at_timestamp(timestamp, offset)
    expected_timestamp = 1735686600000
    assert data[0] == expected_timestamp


def test_get_data_at_timestamp_with_out_of_bounds_offset(data_feed):
    timestamp = 1735686600000
    offset = 100
    with pytest.raises(IndexError):
        data_feed.get_data_at_timestamp(timestamp, offset)


def test_get_data_at_timestamp_with_empty_data_feed(empty_data_feed):
    timestamp = 1735686600000
    data = empty_data_feed.get_data_at_timestamp(timestamp)
    assert len(data) == 0
    assert isinstance(data, np.ndarray)


def test_aggregate_ohlcvs(data_feed):
    end_timestamp = 1735686300000
    data = data_feed.get_data_between_timestamps(end=end_timestamp)
    ohlcv = data_feed._aggregate_ohlcv(data)
    expected_ohlcv = np.array([1735686000000, 191.14, 191.2, 190.38, 190.39, 15729.944])
    assert np.array_equal(ohlcv, expected_ohlcv)


def test_aggregate_ohlcvs_with_empty_data(empty_data_feed):
    with pytest.raises(ValueError):
        empty_data_feed._aggregate_ohlcv(empty_data_feed.get_data_between_timestamps())


def test_resample_with_empty_data_feed(empty_data_feed):
    data = empty_data_feed.get_resampled_data("5m")
    assert len(data) == 0


def test_resample_with_invalid_timeframe(data_feed):
    with pytest.raises(ValueError):
        data_feed.get_resampled_data("5xyz")


def test_resample_data_to_lower_timeframe(data_feed):
    with pytest.raises(ValueError):
        data_feed.get_resampled_data("5s")


def test_resample_data_with_same_timeframe(data_feed):
    with pytest.raises(ValueError):
        data_feed.get_resampled_data("1m")


def test_resample_data_to_15m_timeframe(data_feed):
    resampled_data = data_feed.get_resampled_data("15m")
    expected_resample = np.array(
        [
            [1735686000000, 191.14, 191.2, 190.15, 190.98, 40937.716],
            [1735686900000, 190.97, 191.11, 190.0, 190.49, 28504.939],
            [1735687800000, 190.49, 190.49, 189.2, 189.53, 35837.209],
            [1735688700000, 189.53, 190.04, 189.29, 189.31, 30592.866],
        ]
    )
    assert len(resampled_data) == len(expected_resample)
    assert np.allclose(resampled_data, expected_resample, atol=1e-12)
