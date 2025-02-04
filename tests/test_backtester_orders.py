import pytest


from ccxt.base.errors import InsufficientFunds, BadSymbol, BadRequest


@pytest.fixture
def backtester_with_orders(backtester):
    backtester.create_order("SOL/USDT", "limit", "buy", 1.0, 100.0)
    backtester.create_order("BTC/USDT", "limit", "buy", 0.001, 50000.0)
    backtester.create_order("ETH/USDT", "limit", "buy", 0.1, 3000.0)
    backtester.create_order("SOL/USDT", "limit", "sell", 2.0, 150.0)
    backtester.create_order("SOL/USDT", "limit", "buy", 0.5, 120.0)
    backtester.create_order("SOL/USDT", "limit", "sell", 0.5, 140.0)
    backtester.create_order("ETH/USDT", "limit", "sell", 1.0, 4000.0)
    backtester.create_order("BTC/USDT", "limit", "sell", 0.1, 60000.0)
    backtester.create_order("BTC/USDT", "limit", "buy", 0.002, 55000.0)
    backtester.create_order("ETH/USDT", "limit", "buy", 0.1, 2000.0)
    return backtester


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


def test_fetch_orders_without_symbol(backtester_with_orders):
    orders = backtester_with_orders.fetch_orders()
    assert len(orders) == 10


def test_fetch_orders_without_limit(backtester_with_orders):
    orders = backtester_with_orders.fetch_orders("SOL/USDT")
    assert len(orders) == 4


def test_fetch_orders_with_limit(backtester_with_orders):
    limited_orders = backtester_with_orders.fetch_orders("SOL/USDT", limit=2)
    assert len(limited_orders) == 2


def test_fetch_order_by_id_returns_correct_order(backtester_with_orders):
    order = backtester_with_orders.create_order("SOL/USDT", "limit", "buy", 3.142, 96)
    fetched_order = backtester_with_orders.fetch_order(order["id"])

    assert fetched_order["id"] == order["id"]
    assert fetched_order["symbol"] == order["symbol"]
    assert fetched_order["type"] == order["type"]
    assert fetched_order["side"] == order["side"]
    assert fetched_order["amount"] == order["amount"]
    assert fetched_order["price"] == order["price"]
    assert fetched_order["fee"] == order["fee"]


def test_cancel_order_by_id(backtester_with_orders):
    order = backtester_with_orders.create_order("SOL/USDT", "limit", "buy", 3.142, 96)
    backtester_with_orders.cancel_order(order["id"])
    assert order["status"] == "open"
    cancelled_order = backtester_with_orders.fetch_order(order["id"])
    assert cancelled_order["status"] == "canceled"


def test_fetch_open_orders(backtester_with_orders):
    order = backtester_with_orders.create_order("SOL/USDT", "limit", "buy", 3.142, 96)
    open_orders = backtester_with_orders.fetch_open_orders("SOL/USDT")
    assert len(open_orders) == 5
    backtester_with_orders.cancel_order(order["id"])

    open_orders_post_cancel = backtester_with_orders.fetch_open_orders("SOL/USDT")
    assert len(open_orders_post_cancel) == 4


def test_closed_orders_is_empty(backtester):
    closed_orders = backtester.fetch_closed_orders()
    assert len(closed_orders) == 0
