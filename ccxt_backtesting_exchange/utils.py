from datetime import timedelta


def timeframe_to_timedelta(timeframe: str) -> timedelta:
    """
    Converts a timeframe string (e.g., '1m', '5m', '4h') into a timedelta instance.

    :param timeframe: The timeframe string (e.g., '1m', '5m', '4h',).
    :return: A timedelta instance representing the duration of the timeframe.
    :raises ValueError: If the timeframe string is invalid or unsupported.
    """
    # Extract the numeric value and unit from the timeframe string
    try:
        value = int(timeframe[:-1])
        unit = timeframe[-1]
    except (ValueError, IndexError):
        raise ValueError(f"Invalid timeframe format: {timeframe}")

    unit_map = {
        "s": "seconds",
        "m": "minutes",
        "h": "hours",
        "d": "days",
        "w": "weeks",
    }

    if unit not in unit_map:
        raise ValueError(f"Unsupported unit in timeframe: {unit}")

    # Calculate the total timedelta
    return timedelta(**{unit_map[unit]: value})
