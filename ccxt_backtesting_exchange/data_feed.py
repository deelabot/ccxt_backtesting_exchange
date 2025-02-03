import numpy as np
import json


class DataFeed:

    def __init__(self, file_path: str):
        """
        Initialize the DataFeed by loading ohlcv data from a JSON file.

        :param file_path: Path to the JSON file containing ohlcv data.
        """
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

            self.__data = np.array(data, dtype=np.float64)
        except FileNotFoundError:
            # if file does not exist, create an empty array and raise a warning
            self.__data = np.array([])
            print(f"Warning: File {file_path} not found. DataFeed is empty.")

    def get_data_between_timestamps(
        self, start: int = None, end: int = None, limit: int = None
    ):
        """
        Retrieve raw ohlcvs between two timestamps.

        :param start: Start timestamp in milliseconds (inclusive).
        :param end: End timestamp in milliseconds (exclusive).
        :param limit: Maximum number of records to return. Return all records if None.
        :return: A NumPy structured array containing the filtered ohlcvs.
        """
        if self.__data.size == 0:
            return np.array([])

        timestamps = self.__data[:, 0]  # Extract timestamps from first column
        if start is None:
            mask = timestamps >= timestamps[0]
        else:
            mask = timestamps >= start

        if end is not None:
            mask &= timestamps < end

        filtered_data = self.__data[mask]

        if limit is not None:
            if end is None and start is not None:
                filtered_data = filtered_data[:limit]
            else:
                filtered_data = filtered_data[-limit:]
        return filtered_data

    def _get_data_at_timestamp(self, timestamp: int, offset: int = 0):
        """
        Retrieve ohlcvs at a specific timestamp.

        :param timestamp: The timestamp in milliseconds.
        :param offset: The offset from the timestamp. Positive values looks ahead.
        :return: A NumPy structured array of the ohlcvs at the specified timestamp.
        """
        if self.__data.size == 0:
            return np.array([])

        timestamps = self.__data[:, 0]
        index = np.searchsorted(timestamps, timestamp)
        index += offset
        if index < 0 or index >= len(self.__data):
            raise IndexError("Index out of bounds")
        return self.__data[index]
