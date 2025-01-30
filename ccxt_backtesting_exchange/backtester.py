import pandas as pd
from typing import Dict
from enum import Enum

import ccxt
from ccxt.base.errors import InsufficientFunds


class OrderStatus(Enum):
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELED = "canceled"
    OPEN = "open"


class Backtester(ccxt.Exchange):
    """
    A backtesting exchange class that inherits from the ccxt.Exchange base class
    and implements the ccxt.Exchange unified API.
    """

    def __init__(self, balances: Dict, fee=0):
        super().__init__()

        self._balances = pd.DataFrame(columns=["asset", "free", "used", "total"])
        self._orders = pd.DataFrame(
            columns=[
                "createdAt",
                "symbol",
                "type",
                "side",
                "amount",
                "price",
                "status",
                "updatedAt",
                "fee",
                "params",
            ]
        )
        self._fee = fee
        self.__init_balances(balances)

    def __init_balances(self, balances: Dict):
        """
        Initialize the balances of the backtesting exchange.

        balances: Dict, example: {"BTC": 1, "ETH": 10}
        """
        if not balances:
            return
        updates = pd.DataFrame(
            [
                {
                    "asset": asset,
                    "free": balance,
                    "used": 0,
                    "total": balance,
                }
                for asset, balance in balances.items()
            ]
        )
        if self._balances.empty:
            self._balances = updates
        else:
            self._balances = pd.concat([self._balances, updates], ignore_index=True)

    def __milliseconds(self):
        return 0  # todo: implement clock mechanism for backtesting

    def __get_df_value_by_column(
        self, df: pd.DataFrame, query_column: str, query_value: any, return_column: str
    ) -> any:
        """
        Generic method to get a value from a specific value from a DataFrame.

        :param df: The DataFrame to query.
        :param query_column: The column to query for the specific value.
        :param query_value: The value to search for in the query column.
        :param return_column: The column from which to retrieve the value.

        :return: The queried value from DataFrame.
        :raises: ValueError if query not found.
        """
        # Check if the query column exists in the DataFrame
        if query_column not in df.columns:
            raise ValueError(
                f"Query column '{query_column}' not found in the DataFrame."
            )

        # Check if the return column exists in the DataFrame
        if return_column not in df.columns:
            raise ValueError(
                f"Return column '{return_column}' not found in the DataFrame."
            )

        # Find the rows that match the query_value in the query_column
        filtered_df = df[df[query_column] == query_value]

        if filtered_df.empty:
            raise ValueError(
                f"No rows found where '{query_column}' is '{query_value}'."
            )

        # Retrieve the value from the return_column
        value = filtered_df[return_column].values[0]

        return value

    def __update_df_value_by_column(
        self,
        df: pd.DataFrame,
        query_column: str,
        query_value: any,
        update_column: str,
        new_value: any,
    ) -> None:
        """
        Generic method to update a value in a DataFrame.

        :param df: The DataFrame to update.
        :param query_column: The column where we search for the query_value.
        :param query_value: The value to search for in the query_column.
        :param update_column: The column where the value should be updated.
        :param new_value: The new value to set in the update_column.
        :raises: ValueError if update column is not found, or if no match is found.
        """
        # Check if the query column exists in the DataFrame
        if query_column not in df.columns:
            raise ValueError(
                f"Query column '{query_column}' not found in the DataFrame."
            )

        # Check if the update column exists in the DataFrame
        if update_column not in df.columns:
            raise ValueError(
                f"Update column '{update_column}' not found in the DataFrame."
            )

        # Find the index of the row(s) matching the query value
        mask = df[query_column] == query_value

        if not mask.any():
            raise ValueError(
                f"No rows found where '{query_column}' is '{query_value}'."
            )

        # Update the column value for the matching rows
        df.loc[mask, update_column] += new_value

    def _get_asset_balance(self, asset: str, column: str) -> float:
        """
        Helper method to get the balance of a specific asset by column (.g., free).

        :param asset: The asset to query.
        :param column: The column to retrieve (e.g., 'free' or 'total').
        :return: The balance of the asset in the specified column.
        """
        return self.__get_df_value_by_column(self._balances, "asset", asset, column)

    def _update_asset_balance(self, asset: str, column: str, amount: float) -> None:
        """
        Helper method to update the balance of a specific asset by adding
        or subtracting an amount.

        :param asset: The asset to update.
        :param column: The column to update ('free' or 'total').
        :param amount: The amount to add or subtract.
        """

        # Update the balance by adding/subtracting the amount
        self.__update_df_value_by_column(self._balances, "asset", asset, column, amount)

    def deposit(self, asset: str, amount: float, id=None):
        """
        Deposit an asset to the backtesting exchange.
        """
        self._update_asset_balance(asset, "free", amount)
        self._update_asset_balance(asset, "total", amount)

    def withdraw(self, asset: str, amount: float, id=None):
        """
        Withdraw an asset from the backtesting exchange.
        """
        free_balance = self._get_asset_balance(asset, "free")
        if free_balance < amount:
            raise InsufficientFunds(
                f"Insufficient balance. {asset} balance: {free_balance}"
            )

        self._update_asset_balance(asset, "free", -amount)
        self._update_asset_balance(asset, "total", -amount)

    def fetch_balance(self):
        """
        Fetch the balance of the backtesting exchange.
        """
        return self._balances.set_index("asset").to_dict(orient="index")

    def create_order(
        self, symbol: str, type: str, side: str, amount: float, price: float
    ):
        self._orders.loc[len(self._orders)] = {
            "createdAt": self.__milliseconds(),
            "updatedAt": None,
            "symbol": symbol,
            "side": side,
            "type": type,
            "amount": amount,
            "price": price,
            "fee": amount * price * self._fee,
            "status": OrderStatus.OPEN,
        }
