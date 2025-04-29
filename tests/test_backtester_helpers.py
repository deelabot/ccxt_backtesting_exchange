import pytest
import pandas as pd
from ccxt_backtesting_exchange.backtester import Backtester


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "timestamp": [1735686000000, 1735686060000, 1735686120000],
        "open": [93488.83, 93445.46, 93417.71],
        "high": [93488.84, 93480.5, 93475.45],
        "low": [93445.45, 93405.27, 93417.71],
        "close": [93445.45, 93417.72, 93475.45],
        "volume": [8.3748, 13.65448, 3.38207]
    })

# Testing __get_df_value_by_column


def test_get_value_success(backtester, sample_df):
    result = backtester._Backtester__get_df_value_by_column(
        sample_df, "timestamp", 1735686060000, "close")
    assert result == 93417.72


def test_nonexistent_query_column(backtester, sample_df):
    with pytest.raises(ValueError, match="Query column 'nonexistent' not found in the DataFrame."):
        backtester._Backtester__get_df_value_by_column(
            sample_df, "nonexistent", 1735686060000, "close")


def test_nonexistent_result_column(backtester, sample_df):
    with pytest.raises(ValueError, match="Return column 'nonexistent' not found in the DataFrame."):
        backtester._Backtester__get_df_value_by_column(
            sample_df, "timestamp", 1735686060000, "nonexistent")


def test_nonexistent_query_and_result_column(backtester, sample_df):
    with pytest.raises(ValueError, match="Query column 'nonexistent_query_column' not found in the DataFrame."):
        backtester._Backtester__get_df_value_by_column(
            sample_df, "nonexistent_query_column", 1735686060000, "nonexinonexistent_result_columnstent")


def test_value_not_found(backtester, sample_df):
    with pytest.raises(ValueError, match="No rows found where 'timestamp' is '9999999999999'."):
        backtester._Backtester__get_df_value_by_column(
            sample_df, "timestamp", 9999999999999, "close")


def test_multiple_values(backtester, sample_df):
    new_row = pd.DataFrame([{
        "timestamp": 1735686060000, "open": 93446.00, "high": 93481.00, "low": 93406.00, "close": 93418.00, "volume": 14.000
    }])

    extended_df = pd.concat([sample_df, new_row], ignore_index=True)

    result = backtester._Backtester__get_df_value_by_column(
        extended_df, "timestamp", 1735686060000, "close")
    assert result in [93417.72, 93418.00]  # First matching row is returned

# Testing __set_df_value_by_column


def test_set_value_success(backtester, sample_df):
    backtester._Backtester__set_df_value_by_column(
        sample_df, "timestamp", 1735686060000, "close", 93500.00)
    assert sample_df.loc[sample_df["timestamp"] ==
                         1735686060000, "close"].iloc[0] == 93500.00


def test_set_column_not_found(backtester, sample_df):
    with pytest.raises(ValueError, match="Update column 'nonexistent' not found in the DataFrame."):
        backtester._Backtester__set_df_value_by_column(
            sample_df, "timestamp", 1735686060000, "nonexistent", 93500.00)


def test_set_value_not_found(backtester, sample_df):
    with pytest.raises(ValueError, match="No rows found where 'timestamp' is '9999999999999'."):
        backtester._Backtester__set_df_value_by_column(
            sample_df, "timestamp", 9999999999999, "close", 93500.00)


def test_set_value_on_invalid_column(backtester, sample_df):
    with pytest.raises(ValueError, match="Query column 'nonexistent' not found in the DataFrame."):
        backtester._Backtester__set_df_value_by_column(
            sample_df, "nonexistent", 9999999999999, "close", 93500.00)


def test_set_multiple_values_limit_exceeded(backtester, sample_df):
    new_row = pd.DataFrame([{
        "timestamp": 1735686060000, "open": 93446.00, "high": 93481.00, "low": 93406.00, "close": 93418.00, "volume": 14.000
    }])
    extended_df = pd.concat([sample_df, new_row], ignore_index=True)
    with pytest.raises(ValueError, match="Query matches 2 rows. LIMIT = 1."):
        backtester._Backtester__set_df_value_by_column(
            extended_df, "timestamp", 1735686060000, "close", 93500.00)

# Testing __update_df_value_by_column


def test_update_value_success(backtester, sample_df):
    backtester._Backtester__update_df_value_by_column(
        sample_df, "timestamp", 1735686060000, "close", 10)
    assert sample_df.loc[sample_df["timestamp"] ==
                         1735686060000, "close"].iloc[0] == 93427.72


def test_update_column_not_found(backtester, sample_df):
    with pytest.raises(ValueError, match="Return column 'nonexistent' not found in the DataFrame."):
        backtester._Backtester__update_df_value_by_column(
            sample_df, "timestamp", 1735686060000, "nonexistent", 10)


def test_update_value_not_found(backtester, sample_df):
    with pytest.raises(ValueError, match="No rows found where 'timestamp' is '9999999999999'."):
        backtester._Backtester__update_df_value_by_column(
            sample_df, "timestamp", 9999999999999, "close", 10)


def test_update_multiple_values_limit_exceeded(backtester, sample_df):
    new_row = pd.DataFrame([{
        "timestamp": 1735686060000, "open": 93446.00, "high": 93481.00, "low": 93406.00, "close": 93418.00, "volume": 14.000
    }])
    extended_df = pd.concat([sample_df, new_row], ignore_index=True)
    with pytest.raises(ValueError, match="Query matches 2 rows. LIMIT = 1."):
        backtester._Backtester__update_df_value_by_column(
            extended_df, "timestamp", 1735686060000, "close", 10)
