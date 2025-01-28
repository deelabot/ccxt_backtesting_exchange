import pandas as pd
from typing import Dict

import ccxt
from ccxt.base.errors import InsufficientFunds


class Backtester(ccxt.Exchange):
    """
    A backtesting exchange class that inherits from the ccxt.Exchange and implements the ccxt.Exchange unified API.
    """

    def __init__(self, balances: Dict, fee):
        super().__init__()

        self.balances = pd.DataFrame(columns=["asset", "free", "used", "total"])
        self.fee = fee
        self._init_balances(balances)

    def _init_balances(self, balances: Dict):
        """
        Initialize the balances of the backtesting exchange.

        balances: Dict, example: {"BTC": 1, "ETH": 10}
        """
        updates = pd.DataFrame(
            [
                {"asset": asset, "free": balance, "used": 0, "total": balance}
                for asset, balance in balances.items()
            ]
        )
        self.balances = pd.concat([self.balances, updates], ignore_index=True)

    def _get_asset_balance(self, asset: str, column: str) -> float:
        """
        Helper method to get the balance of a specific asset and column (e.g., 'free' or 'total').

        :param asset: The asset to query.
        :param column: The column to retrieve ('free' or 'total').
        :return: The balance of the asset in the specified column.
        """
        return self.balances.loc[self.balances["asset"] == asset, column].values[0]

    def _update_asset_balance(self, asset: str, column: str, amount: float):
        """
        Helper method to update the balance of a specific asset and column.

        :param asset: The asset to update.
        :param column: The column to update ('free' or 'total').
        :param amount: The amount to add or subtract.
        """
        self.balances.loc[self.balances["asset"] == asset, column] += amount

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
        return self.balances.set_index("asset").to_dict(orient="index")
