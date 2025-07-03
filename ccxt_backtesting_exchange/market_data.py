import ccxt
import pandas as pd
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from tqdm import tqdm

from .utils import timeframe_to_timedelta


class MarketDataCache:
    def __init__(self, exchange_id: str, symbol: str, timeframe="1m"):
        """
        Initialize the MarketDataCache.

        :param exchange_id: The ID of the exchange (e.g., 'binance', 'kraken').
        :param symbol: The trading symbol (e.g., 'BTC/USDT').
        """
        try:
            self.exchange: ccxt.Exchange = getattr(ccxt, exchange_id)()
        except AttributeError:
            raise ValueError(f"Exchange {exchange_id} not supported by ccxt.")

        self.symbol = symbol
        self.timeframe = timeframe
        self.interval = timeframe_to_timedelta(timeframe)
        self.file_path = f"./data/{symbol.replace('/', '_')}_{timeframe}.json".lower()

    def __convert_to_dataframe(self, arr) -> pd.DataFrame:
        """
        Convert the OHLCV array to a Pandas DataFrame with the correct data types.

        :param arr: List of OHLCV data.
        :return: Pandas DataFrame with the correct data types.
        """
        df = pd.DataFrame(
            arr, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = df["timestamp"].astype("int64")
        df.iloc[:, 1:] = df.iloc[:, 1:].astype("float64")
        return df

    def split_gap_into_chunks(
        self, gaps: List[Tuple[datetime, datetime]], max_delta: timedelta
    ) -> List[Tuple[datetime, datetime]]:
        """
        Split a list of gap intervals into smaller chunks based on max_delta.

        :param gaps: List of tuples representing the start and end of gaps.
        :param max_delta: Maximum allowed time delta for a single chunk.
        :return: List of tuples representing the start and end of smaller chunks.
        """
        chunks = []

        for start, end in gaps:
            current_start = start
            while current_start < end:
                current_end = min(current_start + max_delta, end)
                chunks.append((current_start, current_end))
                current_start = current_end

        return chunks

    def fetch_ohlcv(
        self, since: Optional[int] = None, until: Optional[int] = None, limit: int = 100
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data using ccxt.

        :param since: Timestamp in milliseconds to fetch data from (optional).
        :param until: Timestamp in milliseconds to fetch data until (optional).
        :param limit: Number of data points to fetch (default is 100).
        :return: Pandas DataFrame with OHLCV data.
        """

        ohlcv = self.exchange.fetch_ohlcv(
            self.symbol,
            timeframe=self.timeframe,
            since=since,
            limit=limit,
            params={"until": until},
        )
        print(ohlcv)

        if len(ohlcv) == 0:
            return self.__convert_to_dataframe([])

        df = self.__convert_to_dataframe(ohlcv)

        last_fetched_timestamp = df["timestamp"].iloc[-1]
        if last_fetched_timestamp >= until:
            return df
        else:
            return pd.concat(
                [
                    df,
                    self.fetch_ohlcv(
                        since=int(last_fetched_timestamp + 1),
                        until=until,
                        limit=limit,
                    ),
                ],
                ignore_index=True,
            )

    def load_existing_data(self) -> pd.DataFrame:
        """
        Load existing OHLCV data from the JSON file.

        :return: Pandas DataFrame with existing data.
        """
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)

            df = self.__convert_to_dataframe(data)
            return df

        except FileNotFoundError:
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

    def identify_data_gaps(
        self, df: pd.DataFrame, start_time: datetime, end_time: datetime
    ):
        """
        Identify gaps in the OHLCV data.

        :param df: Pandas DataFrame with OHLCV data.
        :param start_time: Start time of the data.
        :param end_time: End time of the data.
        """
        if df.empty:
            return [(start_time, end_time)]

        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("datetime", inplace=True)

        full_range = pd.date_range(
            start=start_time, end=end_time, freq=self.interval, tz=timezone.utc
        )
        missing_timestamps = full_range.difference(df.index)

        if missing_timestamps.empty:
            return []

        missing_intervals = []
        start = missing_timestamps[0]
        prev = missing_timestamps[0]

        for ts in missing_timestamps[1:]:
            if ts - prev == self.interval:
                prev = ts
            else:
                missing_intervals.append((start, prev + self.interval))
                start = ts
                prev = ts

        missing_intervals.append((start, prev + self.interval))
        return missing_intervals

    def save_data(self, df: pd.DataFrame) -> None:
        """
        Save OHLCV data to the JSON file.

        :param df: Pandas DataFrame with OHLCV data.
        """
        df = df.sort_values("timestamp").drop_duplicates(subset="timestamp")
        df.to_json(self.file_path, orient="values")

    def sync(
        self, since: datetime, until: datetime, chunk_size: int = 1000
    ) -> pd.DataFrame:
        """
        Sync the OHLCV data with the exchange.

        :param since: Start time of the data.
        :param until: End time of the data.
        :return: Updated Pandas DataFrame with OHLCV data.
        """
        existing_data = self.load_existing_data()
        gaps = self.identify_data_gaps(existing_data, since, until)
        gaps = self.split_gap_into_chunks(gaps, max_delta=chunk_size * self.interval)

        for start, end in tqdm(gaps, desc="Syncing data"):
            new_data = self.fetch_ohlcv(
                since=int(start.timestamp() * 1000),
                until=int(end.timestamp() * 1000),
                limit=chunk_size,
            )
            if existing_data.empty:
                existing_data = new_data
            else:
                existing_data = pd.concat([existing_data, new_data], ignore_index=True)

        self.save_data(existing_data)
        return existing_data
