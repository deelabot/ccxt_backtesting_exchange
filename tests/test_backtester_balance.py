import pytest
from ccxt.base.errors import InsufficientFunds

from ccxt_backtesting_exchange.backtester import Backtester


@pytest.fixture
def backtester_with_empty_balances(clock):
    return Backtester(balances={}, clock=clock, fee=0.001)


def test_initial_balances(backtester):
    balance = backtester.fetch_balance()
    expected_balance = {
        "BTC": {"free": 1.0, "used": 0, "total": 1.0},
        "ETH": {"free": 5.0, "used": 0, "total": 5.0},
        "SOL": {"free": 10.0, "used": 0, "total": 10.0},
        "USDT": {"free": 10000.0, "used": 0, "total": 10000.0},
    }
    assert balance == expected_balance


def test_initial_balances_empty(backtester_with_empty_balances):
    balance = backtester_with_empty_balances.fetch_balance()
    expected_balance = {}
    assert balance == expected_balance


def test_deposit(backtester):
    backtester.deposit("BTC", 0.5)
    balance = backtester.fetch_balance()
    expected_balance = {
        "BTC": {"free": 1.5, "used": 0, "total": 1.5},
    }
    assert balance["BTC"] == expected_balance["BTC"]


def test_withdraw_success(backtester):
    backtester.withdraw("ETH", 2.0)
    balance = backtester.fetch_balance()
    expected_balance = {
        "ETH": {"free": 3.0, "used": 0, "total": 3.0},
    }
    assert balance["ETH"] == expected_balance["ETH"]


def test_withdraw_insufficient_funds(backtester):
    with pytest.raises(InsufficientFunds):
        backtester.withdraw("SOL", 20.0)


def test_deposit_and_withdraw_on_same_asset(backtester):
    backtester.deposit("SOL", 5.0)
    backtester.withdraw("SOL", 10.0)
    balance = backtester.fetch_balance()
    expected_balance = {
        "SOL": {"free": 5.0, "used": 0, "total": 5.0},
    }
    assert balance["SOL"] == expected_balance["SOL"]


def test_deposit_and_withdraw_on_multiple_assets(backtester):
    backtester.deposit("BTC", 0.3)
    backtester.withdraw("USDT", 500.0)
    backtester.deposit("ETH", 1.0)

    balance = backtester.fetch_balance()
    expected_balance = {
        "BTC": {"free": 1.3, "used": 0, "total": 1.3},
        "ETH": {"free": 6.0, "used": 0, "total": 6.0},
        "SOL": {"free": 10.0, "used": 0, "total": 10.0},
        "USDT": {"free": 9500.0, "used": 0, "total": 9500.0},
    }
    assert balance == expected_balance


def test_create_buy_order_properly_affects_balances(backtester):
    order = backtester.create_order("SOL/USDT", "limit", "buy", 1.0, 200.0)
    balance = backtester.fetch_balance()
    expected_balance = {
        "SOL": {"free": 10, "used": 0, "total": 10},
        "USDT": {"free": 9799.8, "used": 200.2, "total": 10000.0},
        "BTC": {"free": 1, "used": 0, "total": 1},
    }
    assert balance["SOL"] == expected_balance["SOL"]
    assert balance["USDT"] == expected_balance["USDT"]
    assert balance["BTC"] == expected_balance["BTC"]

    assert order["id"] == 0
    assert order["type"] == "limit"


def test_create_sell_order_properly_affects_balances(backtester):
    order = backtester.create_order("SOL/USDT", "market", "sell", 1.0, 200.0)
    balance = backtester.fetch_balance()
    expected_balance = {
        "SOL": {"free": 9, "used": 1, "total": 10},
        "USDT": {"free": 10000.0, "used": 0, "total": 10000.0},
        "BTC": {"free": 1, "used": 0, "total": 1},
    }
    assert balance["SOL"] == expected_balance["SOL"]
    assert balance["USDT"] == expected_balance["USDT"]
    assert balance["BTC"] == expected_balance["BTC"]

    assert order["id"] == 0
    assert order["type"] == "market"
