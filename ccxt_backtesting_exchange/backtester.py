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

    def _get_asset_balance(self, asset: str, column: str) -> float:
        """
        Helper method to get the balance of a specific asset by column (eg. free, used)

        :param asset: The asset to query.
        :param column: The column to retrieve ('free' or 'total').
        :return: The balance of the asset in the specified column.
        """
        return self._balances.loc[self._balances["asset"] == asset, column].values[0]

    def _update_asset_balance(self, asset: str, column: str, amount: float):
        """
        Helper method to update the balance of a specific asset and column.

        :param asset: The asset to update.
        :param column: The column to update ('free' or 'total').
        :param amount: The amount to add or subtract.
        """
        self._balances.loc[self._balances["asset"] == asset, column] += amount

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
