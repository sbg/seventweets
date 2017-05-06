from datetime import datetime
from seventweets.exceptions import BadRequest


def ensure_dt(val):
    """
    Converts query argument to datetime object.

    If None is provided, it will be returned. Otherwise, conversion to in is
    attempted and that int is treated as unix timestamp, which is converted
    to datetime.datetime.

    :param val: Value to convert to datetime.
    :return: datetime object from provided value.
    :raises BadRequest: If provided value could not be converted to datetime.
    """
    if val is None:
        return None
    try:
        int_val = int(val)
    except ValueError:
        raise BadRequest(f'Expected integer, got: {val}')

    try:
        dt_val = datetime.fromtimestamp(int_val)
        return dt_val
    except Exception:
        raise BadRequest(f'Unable to convert {int_val} to datetime.')


def ensure_bool(val):
    """
    Converts query arguments to boolean value.

    If None is provided, it will be returned. Otherwise, value is lowered and
    compared to 'true'. If comparison is truthful, True is returned, otherwise
    False.

    :param val: Value to convert to boolean.
    :return: boolean value
    """
    if val is None:
        return None
    return val.lower() == 'true'
