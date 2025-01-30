import pytest
from ccxt.base.errors import InsufficientFunds, BadSymbol, BadRequest
from ccxt_backtesting_exchange.backtester import Backtester


@pytest.fixture
def backtester():
    return Backtester(
        balances={"BTC": 1.0, "ETH": 5.0, "SOL": 10.0, "USDT": 10000.0}, fee=0.001
    )


def test_create_order_buy_success(backtester):
    order = backtester.create_order("BTC/USDT", "limit", "buy", 0.1, 50000.0)

    assert order["symbol"] == "BTC/USDT"
    assert order["type"] == "limit"
    assert order["side"] == "buy"
    assert order["amount"] == 0.1
    assert order["price"] == 50000.0
    assert order["fee"]["cost"] == 5


def test_create_order_sell_success(backtester):
    order = backtester.create_order("ETH/USDT", "limit", "sell", 1.0, 3000.0)

    assert order["symbol"] == "ETH/USDT"
    assert order["type"] == "limit"
    assert order["side"] == "sell"
    assert order["amount"] == 1.0
    assert order["price"] == 3000.0
    assert order["fee"]["cost"] == 3.0


def test_create_order_invalid_symbol(backtester):
    with pytest.raises(BadSymbol):
        backtester.create_order("INVALID", "limit", "buy", 0.1, 50000.0)


def test_create_order_invalid_order_type(backtester):
    with pytest.raises(BadRequest):
        backtester.create_order("BTC/USDT", "invalid", "buy", 0.1, 50000.0)


def test_create_order_invalid_side(backtester):
    with pytest.raises(BadRequest):
        backtester.create_order("BTC/USDT", "limit", "invalid", 0.1, 50000.0)


def test_create_order_invalid_amount(backtester):
    with pytest.raises(BadRequest):
        backtester.create_order("BTC/USDT", "limit", "buy", -0.1, 50000.0)


def test_create_order_invalid_price(backtester):
    with pytest.raises(BadRequest):
        backtester.create_order("BTC/USDT", "limit", "buy", 0.1, -50000.0)


def test_create_order_insufficient_funds_buy(backtester):
    with pytest.raises(InsufficientFunds):
        backtester.create_order("BTC/USDT", "limit", "buy", 10.0, 50000.0)


def test_create_order_insufficient_funds_sell(backtester):
    with pytest.raises(InsufficientFunds):
        backtester.create_order("BTC/USDT", "limit", "sell", 10.0, 50000.0)
