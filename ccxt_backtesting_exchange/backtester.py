import pandas as pd
from typing import Dict
from enum import Enum

import ccxt
from ccxt.base.errors import InsufficientFunds, BadSymbol, BadRequest, OrderNotFound


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

    def __init__(self, balances: Dict, fee=0.0):
        super().__init__()

        self._balances = pd.DataFrame(columns=["asset", "free", "used", "total"])
        self._orders = pd.DataFrame(
            columns=[
                "datetime",
                "timestamp",
                "lastTradeTimestamp",
                "symbol",
                "type",
                "side",
                "price",
                "amount",
                "status",
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
                    "free": float(balance),
                    "used": 0.0,
                    "total": float(balance),
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

    def __set_df_value_by_column(
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

        if query_column not in df.columns and query_column != "index":
            raise ValueError(
                f"Query column '{query_column}' not found in the DataFrame."
            )

        # Check if the update column exists in the DataFrame
        if update_column not in df.columns:
            raise ValueError(
                f"Update column '{update_column}' not found in the DataFrame."
            )

        # Find the index of the row(s) matching the query value
        if query_column == "index":
            mask = df.index == query_value
        else:
            mask = df[query_column] == query_value

        if not mask.any():
            raise ValueError(
                f"No rows found where '{query_column}' is '{query_value}'."
            )
        new_value = df[update_column].dtype.type(new_value)
        # Update the column value for the matching rows
        df.loc[mask, update_column] = new_value

    def __update_df_value_by_column(
        self,
        df: pd.DataFrame,
        query_column: str,
        query_value: any,
        update_column: str,
        delta: any,
    ) -> None:
        value = self.__get_df_value_by_column(
            df, query_column, query_value, update_column
        )
        new_value = value + delta
        self.__set_df_value_by_column(
            df, query_column, query_value, update_column, new_value
        )

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
        self, symbol: str, order_type: str, side: str, amount: float, price: float
    ) -> any:
        """
        Creates a new order and adds it to the order book.

        :param symbol: The trading pair (e.g., "BTC/USDT").
        :param order_type: The type of order (e.g., "limit", "market").
        :param side: The order side ("buy" or "sell").
        :param amount: The amount of the base asset to trade.
        :param price: The price at which to place the order.
        :raises BadSymbol: If the trading pair is invalid.
        :raises BadRequest: If the order type, side, amount or price is invalid.

        """
        # Validate inputs
        if not isinstance(symbol, str) or "/" not in symbol:
            raise BadSymbol(
                "Invalid symbol format. Expected 'BASE/QUOTE' (e.g., 'BTC/USDT')."
            )

        if order_type not in {"limit", "market"}:
            raise BadRequest("Invalid order type. Expected 'limit' or 'market'.")

        if side not in {"buy", "sell"}:
            raise BadRequest("Invalid side. Expected 'buy' or 'sell'.")

        if not isinstance(amount, (int, float)) or amount <= 0:
            raise BadRequest("Invalid amount. Must be a positive number.")

        if not isinstance(price, (int, float)) or price <= 0:
            raise BadRequest("Invalid price. Must be a positive number.")

        # Calculate fee
        fee_cost = amount * price * self._fee
        base_asset, quote_asset = symbol.split("/")
        fee = {
            "currency": quote_asset,
            "cost": fee_cost,
            "rate": self._fee,
        }

        # Update pending balance
        if side == "buy":
            trade_value = amount * price + fee_cost  # Buyer needs enough quote currency
            if self._get_asset_balance(quote_asset, "free") < trade_value:
                raise InsufficientFunds(
                    f"Insufficient balance: {quote_asset} balance too low."
                )
            self._update_asset_balance(quote_asset, "used", +trade_value)
            self._update_asset_balance(quote_asset, "free", -trade_value)

        else:  # side == "sell"
            if self._get_asset_balance(base_asset, "free") < amount:
                raise InsufficientFunds(
                    f"Insufficient balance: {base_asset} balance too low."
                )
            self._update_asset_balance(base_asset, "used", amount)
            self._update_asset_balance(base_asset, "free", -amount)

        order_id = len(self._orders)
        self._orders.loc[order_id] = {
            "datetime": self.__milliseconds(),
            "timestamp": self.__milliseconds(),
            "lastTradeTimestamp": None,
            "symbol": symbol,
            "type": order_type,
            "side": side,
            "price": price,
            "amount": amount,
            "fee": fee,
            "status": OrderStatus.OPEN,
        }

        return self.fetch_order(order_id)

    def fetch_orders(
        self,
        symbol: str = None,
        since: int = None,
        limit: int = None,
        params: dict = {},
    ):
        """
        Fetches orders for a given symbol.

        :param symbol: The trading pair symbol (e.g., 'BTC/USDT').
        :param since: Timestamp in milliseconds to fetch orders since.
        :param limit: The maximum number of orders to return.
        :param params: Additional parameters specific to the exchange API.
        :return: A list of orders.
        """
        orders = self._orders
        # Filter orders by symbol
        if symbol is not None:
            orders = orders[orders["symbol"] == symbol]

        # Filter orders by since timestamp if provided
        if since is not None:
            orders = orders[orders["timestamp"] >= since]

        for column, value in params.items():
            if column == "until":
                orders = orders[orders["timestamp"] < params["until"]]

            elif column == "id":
                orders = orders[orders.index == params["id"]]
            elif column in orders.columns:
                orders = orders[orders[column] == value]
            else:
                raise ValueError(f"Invalid column '{column}' in params.")

        # Sort orders by timestamp
        orders = orders.sort_values(by="timestamp", ascending=False)

        # Limit the number of orders if limit is provided
        if limit is not None:
            orders = orders.head(limit)

        # Convert DataFrame to list of dictionaries
        orders_list = (
            orders.reset_index()
            .rename(columns={"index": "id"})
            .to_dict(orient="records")
        )
        return orders_list

    def fetch_order(self, id: str, symbol: str = None, params: dict = {}):
        """
        Fetches a single order by its ID.

        :param id: The ID of the order.
        :param symbol: The trading pair symbol (optional).
        :param params: Additional parameters specific to the exchange API (optional).
        :return: The order as a dictionary.
        """
        order = self.fetch_orders(symbol=symbol, params={"id": id, **params})
        if not order or len(order) == 0:
            raise OrderNotFound(f"Order with id '{id}' not found.")
        if len(order) > 1:
            raise OrderNotFound(f"Multiple orders found with id '{id}'.")

        return order[0]

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params: dict = {}):
        return self.fetch_orders(
            symbol, since, limit, {"status": OrderStatus.OPEN, **params}
        )

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params=...):
        return self.fetch_orders(
            symbol, since, limit, {"status": OrderStatus.FILLED, **params}
        )

    def cancel_order(self, id: str, symbol: str = None, params: dict = {}):
        self.__set_df_value_by_column(
            self._orders, "index", id, "status", OrderStatus.CANCELED
        )
