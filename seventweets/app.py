import sys
import time
import click
import signal
import logging
import datetime
import traceback
from flask import Flask, g, current_app
from seventweets import config as configuration
from seventweets.registry import unregister_all
from seventweets.handlers.base import base
from seventweets.handlers.tweets import tweets
from seventweets.handlers.registration import register
from seventweets.db import get_db
from seventweets.migrate import MigrationManager
from seventweets.utils import generate_api_token


LOG_FORMAT = ('%(asctime)-15s %(levelname)s: '
              '%(message)s [%(filename)s:%(lineno)d]')

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
)


logger = logging.getLogger(__name__)


def create_app(_=None):
    """
    Creates and initializes Flask application.

    :return: Created Flask application.
    """
    app = Flask('seventweets')

    app.config.from_object(configuration)

    app.register_blueprint(base, url_prefix='/')
    app.register_blueprint(tweets, url_prefix='/tweets')
    app.register_blueprint(register, url_prefix='/registry')

    @app.shell_context_processor
    def _enhance_shell():
        """
        Adds some utility stuff to flask interactive shell.
        """
        return {
            'db': get_db(),
        }

    @app.cli.command()
    @click.argument('direction', type=click.Choice(['up', 'down']),
                    default='up')
    def migrate(direction):
        """
        Performs database migrations.
        """
        MigrationManager().migrate(direction)

    @app.cli.command()
    @click.argument('name', type=str)
    def create_migration(name):
        try:
            MigrationManager().create_migration(name)
        except ValueError as e:
            logger.error('Failed to generate migration: %s', str(e))
            print(str(e))

    @app.cli.command()
    def generate_token():
        """
        Generates and prints random API token.
        """
        print(generate_api_token())

    @app.cli.command()
    @click.option('-v', '--verbose', default=False,
                  help='Print stacktrace.', is_flag=True)
    @click.option('-t', '--timeout', default=0,
                  help='Maximum number of seconds to try to connect to DB.')
    def test_db(verbose, timeout):
        """
        Tests DB connection by executing simple query.
        """
        end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while True:
            try:
                get_db().test_connection()
            except Exception as e:
                if datetime.datetime.now() < end:
                    time.sleep(0.5)
                    continue
                if verbose:
                    traceback.print_exc()
                else:
                    print(str(e))
                sys.exit(1)
            else:
                break

    @app.cli.command()
    def config():
        """
        Prints configuration. This includes default values and values provided
        as environment variables.

        These config values can be set by setting environment variables.
        Pattern for environment variable names is to uppercase name of the
        config and prefix it with "ST_". So, "db_name" would be "ST_DB_NAME"
        environment variable.
        """
        cfg = current_app.config.get_namespace('ST_')
        for k, v in cfg.items():
            print(f'{k} = {v}')

    @app.teardown_appcontext
    def teardown_appcontext(e):
        """
        Closes the database again at the end of the request.
        """
        if hasattr(g, 'db'):
            g.db.close()

    @app.after_request
    def add_headers(response):
        """
        Add these headers to each response.
        :param response: Response to add headers to.
        """
        response.headers['X-Server'] = 'seventweets'
        return response

    @app.before_first_request
    def register_handlers():
        """
        Performs some initialization before we start serving clients.

        This initialization is here since here we have application context,
        which we do not have until entire app object is ready.
        """
        with app.app_context():
            db = get_db()

        def handler(signum, frame):
            print('in signal handler', signum)
            unregister_all(db)
            sys.exit(0)

        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)

    return app


app = create_app()
