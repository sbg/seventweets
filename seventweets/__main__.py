import click
from flask.cli import FlaskGroup
from seventweets.app import create_app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """
    Management script for seventweets service.
    """
    # If needed, some initialization can be done here, but by default,
    # all is done by click and seventweets Flask app.


if __name__ == '__main__':
    cli()
