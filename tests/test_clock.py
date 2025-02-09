import datetime
import pytest
from ccxt_backtesting_exchange.clock import Clock


@pytest.fixture
def clock():
    start_time = datetime.datetime(2025, 1, 1, 0, 0, 0)
    end_time = datetime.datetime(2025, 1, 1, 20, 0, 0)
    interval = datetime.timedelta(hours=4)
    clock = Clock(start_time, end_time, interval)
    return clock


def test_that_clock_starts_at_beginning(clock):
    assert clock.get_current_time() == datetime.datetime(2025, 1, 1, 0, 0, 0)


def test_that_clock_advances_with_correct_intervals(clock):

    clock.advance()
    assert clock.get_current_time() == datetime.datetime(2025, 1, 1, 4, 0, 0)

    clock.advance()
    clock.advance()
    assert clock.get_current_time() == datetime.datetime(2025, 1, 1, 12, 0, 0)


def test_that_clock_advances_until_end(clock):
    for _ in range(5):
        assert clock.advance()

    assert clock.get_current_time() == datetime.datetime(2025, 1, 1, 20, 0, 0)
    assert not clock.advance()  # Clock should not advance beyond the end time


def test_reset_restarts_clock(clock):

    clock.advance()
    assert clock.get_current_time() == datetime.datetime(2025, 1, 1, 4, 0, 0)

    # Reset the clock and check if it resets to the start time
    clock.reset()
    assert clock.get_current_time() == datetime.datetime(2025, 1, 1, 0, 0, 0)
