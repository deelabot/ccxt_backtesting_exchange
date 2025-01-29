## CCXT Backtesting Exchange
This is a backtesting simulation that should mirror ccxt unified api calls https://docs.ccxt.com/#/

## Installation
```bash
pip install ccxt_backtesting_exchange
```

## Usage
```python
import ccxt
from ccxt_backtesting_exchange import Backtester

exchange = Backtester()
exchange.load_markets()
```

## Development
```bash
git clone
cd ccxt_backtesting_exchange
poetry install

# Run tests
poetry run pytest

# Run linter
poetry run flake8
```