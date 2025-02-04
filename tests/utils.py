import numpy as np


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
