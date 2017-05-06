import os

ST_DB_HOST = 'localhost'
ST_DB_PORT = 5432
ST_DB_USER = 'workshop'
ST_DB_PASS = None
ST_DB_NAME = 'seventweets'
ST_OWN_NAME = None
ST_OWN_ADDRESS = None
ST_API_TOKEN = None


# Set module level config variables by loading them from environment.
for name in list(globals().keys()):
    try:
        if name.startswith('ST_'):
            globals()[name] = os.environ[name]
    except KeyError:
        pass
