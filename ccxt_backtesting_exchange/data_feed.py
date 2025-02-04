import numpy as np
import json

from .utils import timeframe_to_timedelta


class DataFeed:

    def __init__(self, file_path: str, timeframe: str = "1m"):
        """
        Initialize the DataFeed by loading ohlcv data from a JSON file.

        :param file_path: Path to the JSON file containing ohlcv data.
        """
        self.__interval = timeframe_to_timedelta(timeframe)
        self.__RESAMPLE_CACHE = {}
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

            self.__data = np.array(data, dtype=np.float64)
        except FileNotFoundError:
            # if file does not exist, create an empty array and raise a warning
            self.__data = np.array([])
            print(f"Warning: File {file_path} not found. DataFeed is empty.")

    def _aggregate_ohlcv(self, ohlcv: np.ndarray):
        """
        Aggregate a set of ohlcvs into a single ohlcv.

        :param ohlcv: A NumPy structured array containing ohlcvs.
        :return: A single ohlcv aggregated from the input ohlcvs.
        """
        if ohlcv.size == 0:
            raise ValueError("Input ohlcv array is empty")

        timestamps, open_prices, high_prices, low_prices, close_prices, volumes = (
            ohlcv.T
        )

        # Return the aggregated ohlcv
        return np.array(
            [
                timestamps[0],
                open_prices[0],
                high_prices.max(),
                low_prices.min(),
                close_prices[-1],
                volumes.sum(dtype=np.longdouble),
            ]
        )

    def get_data_between_timestamps(
        self,
        start: int = None,
        end: int = None,
        limit: int = None,
        timeframe: str = None,
    ):
        """
        Retrieve raw ohlcvs between two timestamps.

        :param start: Start timestamp in milliseconds (inclusive).
        :param end: End timestamp in milliseconds (exclusive).
        :param limit: Maximum number of records to return. Return all records if None.
        :param timeframe: Resample the data to a new timeframe before returning.
        :return: A NumPy structured array containing the filtered ohlcvs.
        """
        if self.__data.size == 0:
            return np.array([])
        if timeframe is not None:
            data = self.get_resampled_data(timeframe)
        else:
            data = self.__data

        timestamps = data[:, 0]  # Extract timestamps from first column
        if start is None:
            mask = timestamps >= timestamps[0]
        else:
            mask = timestamps >= start

        if end is not None:
            mask &= timestamps < end

        filtered_data = data[mask]

        if limit is not None:
            if end is None and start is not None:
                filtered_data = filtered_data[:limit]
            else:
                filtered_data = filtered_data[-limit:]
        return filtered_data

    def get_data_at_timestamp(self, timestamp: int, offset: int = 0):
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

    def get_resampled_data(self, timeframe: str):
        """
        Resample the data to a new timeframe.

        :param timeframe: The new timeframe to resample to.
        :return: A NumPy structured array containing the resampled ohlcvs.
        """
        interval = timeframe_to_timedelta(timeframe)

        if interval in self.__RESAMPLE_CACHE:
            return self.__RESAMPLE_CACHE[interval]

        if interval < self.__interval:
            raise ValueError("New timeframe must be larger than current timeframe")

        elif interval == self.__interval:
            return self.__data

        if self.__data.size == 0:
            return np.array([])

        resample_milliseconds = int(interval.total_seconds() * 1000)
        timestamps = self.__data[:, 0]

        # Compute the bins: round timestamps down to the nearest interval
        bin_edges = (timestamps // resample_milliseconds) * resample_milliseconds
        unique_bins, bin_indices = np.unique(bin_edges, return_inverse=True)

        # Preallocate array for performance
        aggregated_data = np.zeros(
            (len(unique_bins), self.__data.shape[1]), dtype=np.float64
        )

        for i, bin_val in enumerate(unique_bins):
            mask = bin_edges == bin_val
            grouped_data = self.__data[mask]

            aggregated_data[i, 0] = bin_val
            aggregated_data[i, 1] = grouped_data[0, 1]  # first open, as open
            aggregated_data[i, 2] = np.max(grouped_data[:, 2])
            aggregated_data[i, 3] = np.min(grouped_data[:, 3])
            aggregated_data[i, 4] = grouped_data[-1, 4]  # last close, as close

            aggregated_data[i, 5] = grouped_data[:, 5].sum()

        self.__RESAMPLE_CACHE[interval] = aggregated_data
        return aggregated_data
