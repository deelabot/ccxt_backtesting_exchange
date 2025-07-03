# API Reference

## Backtester Class

The `Backtester` class is the main component that simulates a cryptocurrency exchange environment compatible with CCXT's unified API.

### Constructor

```python
Backtester(balances: Dict, clock: Clock = None, fee: float = 0.0)
```

**Parameters:**
- `balances` (Dict): Initial balances for each asset (e.g., `{"BTC": 1.0, "USDT": 10000.0}`)
- `clock` (Clock, optional): Clock instance for time simulation
- `fee` (float, optional): Trading fee rate (default: 0.0)

### Balance Management

#### `fetch_balance(params={})`

Retrieves the current balance for all assets.

**Returns:** Dictionary with asset balances
```python
{
    "BTC": {"free": 1.0, "used": 0.0, "total": 1.0},
    "USDT": {"free": 10000.0, "used": 0.0, "total": 10000.0}
}
```

#### `deposit(asset: str, amount: float)`

Deposits funds to the exchange.

**Parameters:**
- `asset` (str): Asset symbol (e.g., "BTC")
- `amount` (float): Amount to deposit

#### `withdraw(code: str, amount: float, params={})`

Withdraws funds from the exchange.

**Parameters:**
- `code` (str): Asset symbol
- `amount` (float): Amount to withdraw
- `params` (dict, optional): Additional parameters

**Raises:**
- `InsufficientFunds`: If balance is insufficient

### Order Management

#### `create_order(symbol: str, type: str, side: str, amount: float, price: float, params={})`

Creates a new order.

**Parameters:**
- `symbol` (str): Trading pair (e.g., "BTC/USDT")
- `type` (str): Order type ("limit" or "market")
- `side` (str): Order side ("buy" or "sell")
- `amount` (float): Order amount
- `price` (float): Order price
- `params` (dict, optional): Additional parameters

**Returns:** Order dictionary with order details

**Raises:**
- `BadSymbol`: Invalid symbol format
- `BadRequest`: Invalid order parameters
- `InsufficientFunds`: Insufficient balance
- `OrderImmediatelyFillable`: For postOnly orders that would fill immediately

#### `cancel_order(id: str, symbol: str = None, params={})`

Cancels an existing order.

**Parameters:**
- `id` (str): Order ID
- `symbol` (str, optional): Trading pair
- `params` (dict, optional): Additional parameters

**Raises:**
- `OrderNotFound`: Order not found
- `BadRequest`: Order already closed/canceled

#### `fetch_orders(symbol: str = None, since: int = None, limit: int = None, params={})`

Fetches orders with optional filtering.

**Parameters:**
- `symbol` (str, optional): Trading pair filter
- `since` (int, optional): Timestamp filter
- `limit` (int, optional): Maximum number of orders
- `params` (dict, optional): Additional filters

**Returns:** List of order dictionaries

#### `fetch_order(id: str, symbol: str = None, params={})`

Fetches a single order by ID.

**Parameters:**
- `id` (str): Order ID
- `symbol` (str, optional): Trading pair
- `params` (dict, optional): Additional parameters

**Returns:** Order dictionary

**Raises:**
- `OrderNotFound`: Order not found

#### `fetch_open_orders(symbol: str, since=None, limit=None, params={})`

Fetches open orders for a symbol.

**Parameters:**
- `symbol` (str): Trading pair
- `since` (int, optional): Timestamp filter
- `limit` (int, optional): Maximum number of orders
- `params` (dict, optional): Additional parameters

**Returns:** List of open order dictionaries

#### `fetch_closed_orders(symbol=None, since=None, limit=None, params={})`

Fetches closed orders.

**Parameters:**
- `symbol` (str, optional): Trading pair filter
- `since` (int, optional): Timestamp filter
- `limit` (int, optional): Maximum number of orders
- `params` (dict, optional): Additional parameters

**Returns:** List of closed order dictionaries

#### `fetch_my_trades(symbol=None, since=None, limit=None, params={})`

Fetches trade history (aliases to fetch_closed_orders).

**Parameters:**
- `symbol` (str, optional): Trading pair filter
- `since` (int, optional): Timestamp filter
- `limit` (int, optional): Maximum number of trades
- `params` (dict, optional): Additional parameters

**Returns:** List of trade dictionaries

### Market Data

#### `fetch_ticker(symbol: str, params={})`

Fetches current ticker data for a symbol.

**Parameters:**
- `symbol` (str): Trading pair
- `params` (dict, optional): Additional parameters

**Returns:** Ticker dictionary
```python
{
    "symbol": "BTC/USDT",
    "timestamp": 1640995200000,
    "datetime": "2024-01-01 00:00:00",
    "high": 47500.0,
    "low": 46500.0,
    "last": 47200.0,
    "open": 47000.0,
    "close": 47200.0,
    "baseVolume": 1.5,
    "change": 200.0,
    "percentage": 0.426,
    "average": 47100.0
}
```

**Raises:**
- `BadSymbol`: No data feed found for symbol

#### `fetch_tickers(symbols=None, params={})`

Fetches tickers for multiple symbols.

**Parameters:**
- `symbols` (list, optional): List of symbols (default: all available)
- `params` (dict, optional): Additional parameters

**Returns:** List of ticker dictionaries

#### `fetch_ohlcv(symbol: str, timeframe="1m", since=None, limit=100, params={})`

Fetches OHLCV data for a symbol.

**Parameters:**
- `symbol` (str): Trading pair
- `timeframe` (str, optional): Timeframe (default: "1m")
- `since` (int, optional): Start timestamp
- `limit` (int, optional): Maximum number of candles
- `params` (dict, optional): Additional parameters (supports "until")

**Returns:** List of OHLCV arrays `[timestamp, open, high, low, close, volume]`

**Raises:**
- `BadSymbol`: No data feed found for symbol

### Data Feed Management

#### `add_data_feed(symbol: str, timeframe: str, file_path: str)`

Adds a data feed for a trading pair.

**Parameters:**
- `symbol` (str): Trading pair (e.g., "BTC/USDT")
- `timeframe` (str): Data timeframe (e.g., "1m", "1h")
- `file_path` (str): Path to JSON data file

**Raises:**
- `NameError`: Data feed already exists for symbol

### Time Management

#### `tick()`

Advances the simulation by one time step and processes order fills.

**Returns:** Boolean indicating if simulation should continue

#### `milliseconds()`

Gets the current simulation time in milliseconds.

**Returns:** Unix timestamp in milliseconds

#### `timestamp()`

Gets the current simulation time as a formatted string.

**Returns:** Datetime string in format "YYYY-MM-DD HH:MM:SS"

### Order Processing

#### `fill_orders()`

Processes and fills orders based on current market data. Called automatically during `tick()`.

## Clock Class

Manages time simulation for backtesting.

### Constructor

```python
Clock(start_time: datetime, end_time: datetime, interval: timedelta)
```

**Parameters:**
- `start_time` (datetime): Starting time for simulation
- `end_time` (datetime): Ending time for simulation
- `interval` (timedelta): Time step for each tick

### Methods

#### `tick()`

Advances the clock by one interval.

**Returns:** Boolean indicating if end time has been reached

#### `get_current_time()`

Gets the current simulation time.

**Returns:** Current datetime

#### `epoch()`

Gets the current time as Unix timestamp in milliseconds.

**Returns:** Integer timestamp

#### `datetime()`

Gets the current time as a formatted string.

**Returns:** Datetime string

#### `reset()`

Resets the clock to the start time.

## DataFeed Class

Handles historical market data loading and querying.

### Constructor

```python
DataFeed(file_path: str, timeframe: str = "1m")
```

**Parameters:**
- `file_path` (str): Path to JSON data file
- `timeframe` (str, optional): Data timeframe (default: "1m")

### Methods

#### `get_data_at_timestamp(timestamp: int, offset: int = 0)`

Gets OHLCV data at a specific timestamp.

**Parameters:**
- `timestamp` (int): Target timestamp in milliseconds
- `offset` (int, optional): Offset from timestamp

**Returns:** OHLCV array `[timestamp, open, high, low, close, volume]`

#### `get_data_between_timestamps(start=None, end=None, limit=None, timeframe=None)`

Gets OHLCV data between timestamps.

**Parameters:**
- `start` (int, optional): Start timestamp
- `end` (int, optional): End timestamp
- `limit` (int, optional): Maximum number of records
- `timeframe` (str, optional): Resample to different timeframe

**Returns:** Array of OHLCV data

#### `get_resampled_data(timeframe: str)`

Resamples data to a different timeframe.

**Parameters:**
- `timeframe` (str): Target timeframe

**Returns:** Resampled OHLCV array

## MarketDataCache Class

Utility class for collecting real market data from exchanges.

### Constructor

```python
MarketDataCache(exchange_id: str, symbol: str, timeframe="1m")
```

**Parameters:**
- `exchange_id` (str): CCXT exchange ID (e.g., "binance")
- `symbol` (str): Trading pair
- `timeframe` (str, optional): Data timeframe

### Methods

#### `sync(since: datetime, until: datetime, chunk_size: int = 1000)`

Synchronizes market data for a time period.

**Parameters:**
- `since` (datetime): Start time
- `until` (datetime): End time
- `chunk_size` (int, optional): Data chunk size

**Returns:** Pandas DataFrame with collected data

#### `load_existing_data()`

Loads existing data from file.

**Returns:** Pandas DataFrame with existing data

#### `save_data(df: pd.DataFrame)`

Saves data to file.

**Parameters:**
- `df` (pd.DataFrame): Data to save

## Utility Functions

### `timeframe_to_timedelta(timeframe: str)`

Converts timeframe string to timedelta object.

**Parameters:**
- `timeframe` (str): Timeframe string (e.g., "1m", "1h", "1d")

**Returns:** timedelta object

**Raises:**
- `ValueError`: Invalid timeframe format

## Data Formats

### OHLCV Data Format

Market data should be provided as JSON arrays:

```json
[
  [timestamp, open, high, low, close, volume],
  [1640995200000, 47000.0, 47500.0, 46500.0, 47200.0, 1.5],
  ...
]
```

### Order Format

Orders are represented as dictionaries:

```python
{
    "id": 0,
    "datetime": "2024-01-01 00:00:00",
    "timestamp": 1640995200000,
    "lastTradeTimestamp": None,
    "symbol": "BTC/USDT",
    "type": "limit",
    "side": "buy",
    "price": 47000.0,
    "amount": 0.1,
    "status": "open",
    "fee": {
        "currency": "USDT",
        "cost": 4.7,
        "rate": 0.001
    }
}
```

## Error Handling

The library uses CCXT's exception classes:

- `InsufficientFunds`: Insufficient balance for operation
- `BadSymbol`: Invalid trading pair format
- `BadRequest`: Invalid request parameters
- `OrderNotFound`: Order not found
- `OrderImmediatelyFillable`: Order would fill immediately (postOnly)

## Order Status

Orders can have the following statuses:

- `"open"`: Order is active and waiting to be filled
- `"filled"`: Order has been completely filled
- `"partially_filled"`: Order has been partially filled
- `"canceled"`: Order has been canceled