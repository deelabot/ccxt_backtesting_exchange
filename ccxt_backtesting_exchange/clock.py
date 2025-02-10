import datetime


class Clock:
    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        interval: datetime.timedelta,
    ):
        """
        Initialize the clock with a start time, end time, and time step.

        :param start_time: The starting time of the backtest.
        :param end_time: The ending time of the backtest.
        :param interval: The time interval for each step (e.g., 1 second, 1 minute).
        """
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        self.current_time = start_time

    def tick(self) -> bool:
        """
        Advance the clock by the time step.

        :return: True if the clock has not reached the end time, False otherwise.
        """
        self.current_time += self.interval
        return self.current_time <= self.end_time

    def get_current_time(self) -> datetime.datetime:
        """
        Get the current time of the clock.

        :return: The current time as a datetime object.
        """
        return self.current_time

    def epoch(self) -> int:
        """
        Get the epoch time of the clock in milliseconds.

        :return: The current time in milliseconds.
        """
        return int(self.current_time.timestamp() * 1000)

    def datetime(self) -> str:
        """
        Get the current time of the clock as a string.

        :return: The current time as a string.
        """
        return self.current_time.strftime("%Y-%m-%d %H:%M:%S")

    def reset(self):
        """
        Reset the clock to the start time.
        """
        self.current_time = self.start_time
