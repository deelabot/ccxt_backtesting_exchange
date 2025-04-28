# CCXT Backtesting Exchange

CCXT Backtesting Exchange is a Python simulation package designed for backtesting trading strategies while mirroring CCXT’s unified API calls. This allows traders and developers to test strategies in a controlled environment before deploying them in live markets.

For more details on CCXT, visit the official documentation: [CCXT Docs](https://docs.ccxt.com/#/).

## Installation

To install the package, run the following command:

```bash
pip install ccxt_backtesting_exchange
```

## Usage

Initialize the backtester as shown below.

### Backtester Setup

```python
import ccxt
from datetime import datetime, timedelta
from ccxt_backtesting_exchange import Backtester, Clock

start_date = datetime(2024, 3, 10, 23, 30)
end_date = datetime(2024, 3, 10, 23, 59)

clock = Clock(
    start_time=start_date,
    end_time=end_date,
    interval=timedelta(minutes=1),  # Simulation interval, same as OHLC interval
)

backtester = Backtester(
    balances={"BTC": 1.0, "ETH": 5.0, "SOL": 10.0, "USDT": 10000.0},  # Starting balance
    clock=clock,
    fee=0.001,  # Transaction fee if applicable
)
```

### Load Backtest Data

Download OHLC dataset from any preferred source and load it into the CCXT backtester. Once the data feed is added, the backtester is ready for use.

```python
backtester.add_data_feed(
    "SOL/USDT", "1m", "./data/test-sol-data.json"
)
```

### Consume Backtesting APIs

The backtester supports various CCXT-like API calls for interacting with the simulated trading environment.

#### Fetch Balance
```python
backtester.fetch_balance()
```

#### Deposit Funds
```python
backtester.deposit("BTC", amount=0.5)
```

#### Withdraw Funds
```python
backtester.withdraw("ETH", amount=2.0)
```

#### Create Order

Order types can be either 'limit' or 'market', and sides can be 'buy' or 'sell'.

```python
backtester.create_order("SOL/USDT", type="limit", side="buy", amount=1.0, price=200.0)
```

#### Cancel Order
```python
backtester.cancel_order(id=1, symbol="SOL/USDT")
```

### Other Available Methods

The backtester supports additional trading-related methods:

```python
backtester.fetch_orders()
backtester.fetch_order(order_id)
backtester.fetch_open_orders()
backtester.fetch_closed_orders()
backtester.fetch_my_trades()
backtester.fetch_ticker("SOL/USDT")
backtester.fetch_tickers()
backtester.fetch_ohlcv("SOL/USDT", timeframe="1m")
```

## Development

Contributions are welcome! If you’d like to improve the project, please open an issue first to discuss your changes.

### Project Setup

Clone the repository and install dependencies using Poetry:

```bash
git clone https://github.com/deelabot/ccxt_backtesting_exchange
cd ccxt_backtesting_exchange
poetry install
```

### Running Tests

Ensure that all tests pass before submitting a pull request:

```bash
poetry run pytest
```

### Linting

Maintain code quality by running:

```bash
poetry run flake8
```

## License

This project is licensed under the MIT License. See the LICENSE file for details. [Yet to determine the project license]

