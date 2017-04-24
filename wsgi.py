import yaml
import logging
from flask import Flask

from seventweets.server import Server
from seventweets.tweets_blueprint import tweets_blueprint
from seventweets.register_blueprint import register_blueprint


logger = logging.getLogger(__name__)


class MyFlask(Flask):
    """
    Custom Flask class. Instantiates and runs Server before app.run()
    When loading different server configs, path to config needs to be changed
    """
    def __init__(self, *args, **kwargs):
        cfg = None
        with open("config/server1.yaml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        server_name = cfg['server']['server_name']
        database = cfg['server']['database']
        my_address = cfg['server']['my_address']
        serving_at_port = cfg['server']['serving_at_port']
        connect_to = cfg['server']['connect_to']
        server = Server(
            server_name=server_name,
            database=database,
            my_address=my_address,
            serving_at_port=serving_at_port,
            connect_to=connect_to
        )
        server.run(production=True)
        super(MyFlask, self).__init__(*args, **kwargs)


application = MyFlask(__name__)
application.register_blueprint(register_blueprint)
application.register_blueprint(tweets_blueprint)


if __name__ == "__main__":
    application.run()
