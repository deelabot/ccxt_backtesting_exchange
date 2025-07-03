# CCXT Backtesting Exchange

A sophisticated Python library for backtesting cryptocurrency trading strategies using CCXT's unified API. This library provides a complete simulation environment that replicates real exchange behavior, allowing developers to test strategies with historical data before deploying them live.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## Features

- **CCXT Compatible**: Full compatibility with CCXT's unified API
- **Realistic Trading Simulation**: Accurate order matching, balance management, and fee calculation
- **Multiple Data Sources**: Support for custom OHLCV data feeds
- **Advanced Order Types**: Market and limit orders with realistic fill simulation
- **Time-Based Simulation**: Precise time control for backtesting scenarios
- **Comprehensive Testing**: Extensive test coverage for reliability

## Installation

```bash
pip install ccxt-backtesting-exchange
```

## Quick Start

```python
from datetime import datetime, timedelta, timezone
from ccxt_backtesting_exchange import Backtester, Clock

# Set up time range for backtesting
start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

# Create a clock for time simulation
clock = Clock(
    start_time=start_time,
    end_time=end_time,
    interval=timedelta(minutes=1)
)

# Initialize backtester with starting balances
backtester = Backtester(
    balances={
        "BTC": 1.0,
        "ETH": 10.0,
        "USDT": 50000.0
    },
    clock=clock,
    fee=0.001  # 0.1% trading fee
)

# Add market data
backtester.add_data_feed("BTC/USDT", "1m", "./data/btc_usdt_1m.json")

# Start trading
order = backtester.create_order("BTC/USDT", "limit", "buy", 0.1, 45000.0)
print(f"Order created: {order['id']}")

# Simulate time progression
while backtester.tick():
    # Your trading logic here
    balance = backtester.fetch_balance()
    print(f"Current time: {backtester.timestamp()}")
    print(f"BTC balance: {balance.get('BTC', {}).get('free', 0)}")
```

## Core Components

### Backtester

The main class that simulates a cryptocurrency exchange:

```python
backtester = Backtester(
    balances={"BTC": 1.0, "USDT": 10000.0},
    clock=clock,
    fee=0.001
)
```

### Clock

Manages time simulation for backtesting:

```python
clock = Clock(
    start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2024, 1, 31, tzinfo=timezone.utc),
    interval=timedelta(minutes=1)
)
```

### DataFeed

Handles historical market data:

```python
# Data should be in JSON format: [[timestamp, open, high, low, close, volume], ...]
backtester.add_data_feed("BTC/USDT", "1m", "./data/btc_data.json")
```

## Trading Operations

### Balance Management

```python
# Check balances
balance = backtester.fetch_balance()
print(balance)
# Output: {'BTC': {'free': 1.0, 'used': 0.0, 'total': 1.0}, ...}

# Deposit funds
backtester.deposit("USDT", 1000.0)

# Withdraw funds
backtester.withdraw("BTC", 0.5)
```

### Order Management

```python
# Create limit order
order = backtester.create_order(
    symbol="BTC/USDT",
    type="limit",
    side="buy",
    amount=0.1,
    price=45000.0
)

# Create market order
market_order = backtester.create_order(
    symbol="BTC/USDT",
    type="market",
    side="sell",
    amount=0.05,
    price=45000.0  # Price for market orders is used for fee calculation
)

# Cancel order
backtester.cancel_order(order['id'])

# Fetch orders
all_orders = backtester.fetch_orders("BTC/USDT")
open_orders = backtester.fetch_open_orders("BTC/USDT")
closed_orders = backtester.fetch_closed_orders("BTC/USDT")
```

### Market Data

```python
# Get current ticker
ticker = backtester.fetch_ticker("BTC/USDT")
print(ticker)
# Output: {'symbol': 'BTC/USDT', 'last': 45000.0, 'high': 46000.0, ...}

# Get OHLCV data
ohlcv = backtester.fetch_ohlcv("BTC/USDT", "1m", limit=100)

# Get all tickers
tickers = backtester.fetch_tickers()
```

## Advanced Features

### Time Control

```python
# Advance time manually
success = backtester.tick()  # Returns False when end time reached

# Get current time
current_time = backtester.milliseconds()  # Unix timestamp in milliseconds
current_datetime = backtester.timestamp()  # Human-readable datetime

# Reset clock
backtester.clock.reset()
```

### Order Execution

Orders are automatically filled when market conditions are met:

- **Limit orders**: Filled when market price reaches the order price
- **Market orders**: Filled immediately at current market price
- **Fee calculation**: Applied based on the configured fee rate

### Data Management

```python
# Add multiple data feeds
backtester.add_data_feed("BTC/USDT", "1m", "./data/btc_1m.json")
backtester.add_data_feed("ETH/USDT", "1m", "./data/eth_1m.json")

# Access data feed directly
data_feed = backtester._data_feeds["BTC/USDT"]
current_candle = data_feed.get_data_at_timestamp(backtester.milliseconds())
```

## Data Format

Market data should be provided in JSON format as arrays of OHLCV data:

```json
[
  [1640995200000, 47000.0, 47500.0, 46500.0, 47200.0, 1.5],
  [1640995260000, 47200.0, 47300.0, 46800.0, 47000.0, 2.1],
  ...
]
```

Each array represents: `[timestamp, open, high, low, close, volume]`

## Market Data Collection

Use the `MarketDataCache` class to collect real market data:

```python
from ccxt_backtesting_exchange import MarketDataCache
from datetime import datetime, timezone

# Initialize data collector
collector = MarketDataCache(
    exchange_id="binance",
    symbol="BTC/USDT", 
    timeframe="1m"
)

# Sync data for a specific period
start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
end_time = datetime(2024, 1, 31, tzinfo=timezone.utc)

data = collector.sync(start_time, end_time)
print(f"Collected {len(data)} candles")
```

## Testing

Run the test suite:

```bash
# Install development dependencies
poetry install

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=ccxt_backtesting_exchange

# Run specific test file
poetry run pytest tests/test_backtester_balance.py
```

## Development

### Project Structure

```
ccxt_backtesting_exchange/
├── ccxt_backtesting_exchange/
│   ├── __init__.py
│   ├── backtester.py      # Main backtester class
│   ├── clock.py           # Time simulation
│   ├── data_feed.py       # Market data handling
│   ├── market_data.py     # Data collection utilities
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
├── data/                  # Sample data files
└── pyproject.toml         # Project configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Run the test suite
6. Submit a pull request

### Code Quality

```bash
# Format code
poetry run black .

# Check linting
poetry run flake8

# Run type checking (if using mypy)
poetry run mypy ccxt_backtesting_exchange/
```

## Complete Example

Here's a comprehensive example showing how to set up and run a backtest:

```python
from datetime import datetime, timedelta, timezone
from ccxt_backtesting_exchange import Backtester, Clock

# Set up time range for backtesting
start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

# Create clock for time simulation
clock = Clock(
    start_time=start_time,
    end_time=end_time,
    interval=timedelta(minutes=1)
)

# Initialize backtester with starting balances
backtester = Backtester(
    balances={
        "BTC": 1.0,
        "ETH": 10.0,
        "USDT": 50000.0
    },
    clock=clock,
    fee=0.001  # 0.1% trading fee
)

# Add market data feeds
backtester.add_data_feed("BTC/USDT", "1m", "./data/btc_usdt_1m.json")
backtester.add_data_feed("ETH/USDT", "1m", "./data/eth_usdt_1m.json")

print("Starting backtest...")

# Main backtesting loop
while backtester.tick():
    current_time = backtester.timestamp()
    
    # Get current market data
    btc_ticker = backtester.fetch_ticker("BTC/USDT")
    eth_ticker = backtester.fetch_ticker("ETH/USDT")
    
    # Get current balances
    balance = backtester.fetch_balance()
    
    # Your trading logic here
    if btc_ticker['last'] < 45000:  # Example: buy BTC if price is low
        try:
            order = backtester.create_order("BTC/USDT", "market", "buy", 0.01, btc_ticker['last'])
            print(f"Bought BTC at {btc_ticker['last']}")
        except Exception as e:
            print(f"Buy failed: {e}")
    
    # Check and fill any pending orders
    open_orders = backtester.fetch_open_orders("BTC/USDT")
    if open_orders:
        print(f"Open orders: {len(open_orders)}")

print("Backtest completed!")

# Print final results
final_balance = backtester.fetch_balance()
print("Final balances:")
for asset, balance_info in final_balance.items():
    print(f"  {asset}: {balance_info['total']:.6f}")
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [API Reference](docs/api.md)
- **Issues**: [GitHub Issues](https://github.com/deelabot/ccxt_backtesting_exchange/issues)
- **Discussions**: [GitHub Discussions](https://github.com/deelabot/ccxt_backtesting_exchange/discussions)

## Acknowledgments

- Built on top of the excellent [CCXT](https://github.com/ccxt/ccxt) library
- Inspired by the need for accurate cryptocurrency trading backtesting