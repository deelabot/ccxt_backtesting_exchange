import numpy as np
import pytest


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


def assert_dict_close(dict1: dict, dict2: dict, rel=1e-9, abs=1e-9):
    """
    Recursively compare two dictionaries for equality, .

    Parameters:
        dict1 (dict): First dictionary.
        dict2 (dict): Second dictionary.
        rel (float): Relative tolerance for pytest.approx (default is 1e-9).
        abs (float): Absolute tolerance for pytest.approx (default is 1e-9).
    """
    # Check if keys are the same
    assert (
        dict1.keys() == dict2.keys()
    ), f"Keys do not match: {dict1.keys()} != {dict2.keys()}"

    # Recursively compare values
    for key in dict1:
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            # If both values are dictionaries, recurse
            assert_dict_close(dict1[key], dict2[key], rel=rel, abs=abs)
        elif isinstance(dict1[key], (float, int)) and isinstance(
            dict2[key], (float, int)
        ):
            # If values are numeric, use pytest.approx for comparison
            assert dict1[key] == pytest.approx(
                dict2[key], rel=rel, abs=abs
            ), f"Value mismatch for key '{key}': {dict1[key]} != {dict2[key]}"
        else:
            assert (
                dict1[key] == dict2[key]
            ), f"Value mismatch for key '{key}': {dict1[key]} != {dict2[key]}"
