import datetime
import pytest
from ccxt_backtesting_exchange.clock import Clock


@pytest.fixture
def clock():
    start_time = datetime.datetime(2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2025, 1, 1, 20, 0, 0, tzinfo=datetime.timezone.utc)
    interval = datetime.timedelta(hours=4)
    clock = Clock(start_time, end_time, interval)
    return clock


def test_that_clock_starts_at_beginning(clock):
    assert clock.get_current_time() == datetime.datetime(
        2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert clock.epoch() == 1735689600000
    assert clock.datetime() == "2025-01-01 00:00:00"


def test_that_clock_advances_with_correct_intervals(clock):

    clock.tick()
    assert clock.get_current_time() == datetime.datetime(
        2025, 1, 1, 4, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert clock.epoch() == 1735704000000
    assert clock.datetime() == "2025-01-01 04:00:00"

    clock.tick()
    clock.tick()
    assert clock.get_current_time() == datetime.datetime(
        2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert clock.epoch() == 1735732800000
    assert clock.datetime() == "2025-01-01 12:00:00"


def test_that_clock_advances_until_end(clock):
    for _ in range(5):
        assert clock.tick()

    assert clock.get_current_time() == datetime.datetime(
        2025, 1, 1, 20, 0, 0, tzinfo=datetime.timezone.utc
    )
    assert not clock.tick()  # Clock should not advance beyond the end time


def test_reset_restarts_clock(clock):

    clock.tick()
    assert clock.get_current_time() == datetime.datetime(
        2025, 1, 1, 4, 0, 0, tzinfo=datetime.timezone.utc
    )

    # Reset the clock and check if it resets to the start time
    clock.reset()
    assert clock.get_current_time() == datetime.datetime(
        2025, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
    )
