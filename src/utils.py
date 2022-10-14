"""
Utils
"""

# Standard Library
import json


def _load_query(query_file: str) -> str:
    """
    Load the advanced query from a json file.

    :param query_file: path to the json file.
    :return: advanced query in json string format (single line).
    """
    with open(query_file, 'r', encoding='utf-8') as file_pointer:
        query = json.load(file_pointer)
    # return single line json string
    return json.dumps(query)


def _human_readable_time(seconds: float) -> str:
    """
    Convert seconds to a human-readable time.

    >>> _human_readable_time(0)
    '0s'
    >>> _human_readable_time(1)
    '1s'
    >>> _human_readable_time(60)
    '1m 0s'
    >>> _human_readable_time(61)
    '1m 1s'
    >>> _human_readable_time(3600)
    '1h 0m 0s'
    >>> _human_readable_time(3601)
    '1h 0m 1s'
    >>> _human_readable_time(3661)
    '1h 1m 1s'
    >>> _human_readable_time(86400)
    '1d 0h 0m 0s'
    >>> _human_readable_time(86401)
    '1d 0h 0m 1s'
    >>> _human_readable_time(86461)
    '1d 0h 1m 1s'
    >>> _human_readable_time(90061)
    '1d 1h 1m 1s'
    >>> _human_readable_time(90061.123)
    '1d 1h 1m 1s'
    >>> _human_readable_time(86400 * 2)
    '2d 0h 0m 0s'

    :param seconds: number of seconds.
    :return: human-readable time.
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if days > 0:
        return f'{days:.0f}d {hours:.0f}h {minutes:.0f}m {seconds:.0f}s'
    if hours > 0:
        return f'{hours:.0f}h {minutes:.0f}m {seconds:.0f}s'
    if minutes > 0:
        return f'{minutes:.0f}m {seconds:.0f}s'
    return f'{seconds:.0f}s'
