import functools
from flask import request, current_app
from seventweets.exceptions import Unauthorized

API_TOKEN_KEY = 'X-Api-Token'


def auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        token = current_app.config['ST_API_TOKEN']
        # In case API token was no provided, decline all call to protected
        # view. Better safe then sorry.
        if token is None:
            raise Unauthorized('Server not configured with API token.')
        if request.headers.get(API_TOKEN_KEY, None) != token:
            raise Unauthorized('Invalid API token.')
        return f(*args, **kwargs)
    return wrapper
