import yaml
import signal
import logging
from flask import Flask

from seventweets.config import g
from seventweets import operations
from seventweets.models import Registry, Database
from seventweets.tweets_blueprint import tweets_blueprint
from seventweets.register_blueprint import register_blueprint

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(register_blueprint)
app.register_blueprint(tweets_blueprint)


class Server:
    """
    Template for server
    """

    def __init__(self, server_name, database, serving_at_port,
                 my_address, connect_to=None):
        """
        Initialize server with supplied attributes
        :param server_name: Unique server name - username
        :param my_address: Address of the server machine
        :param serving_at_port: Port on which server is serving
        :param database:  Server's db
        :param connect_to: Address of one server already in twitter network
        """
        self.server_name = server_name
        self.my_address = my_address
        self.serving_at_port = serving_at_port
        self.database = database
        self.connect_to = connect_to

    def execute(self):
        """
        Add attributes to global object g and connect to others in network.
        If connect_to is not supplied then the server is first in the network.
        :return:
        """
        g.my_name = self.server_name
        g.port = self.serving_at_port
        g.db_name = self.database
        g.my_address = self.my_address + ':' + g.port
        g.registry = Registry(name=g.my_name, address=g.my_address)
        try:
            with open("config/db_conf.yaml", 'r') as ymlfile:
                cfg = yaml.load(ymlfile)
                g.db = Database(
                    user=cfg['user'],
                    host=cfg['host'],
                    unix_sock=cfg['unix_sock'],
                    port=cfg['port'],
                    database=cfg['database'],
                    password=cfg['password'],
                    ssl=cfg['ssl'],
                    timeout=cfg['timeout']
                    )
        except FileNotFoundError:
            # if conf file doesn't exist assume local db exist
            g.db = Database(user=g.my_name, database=g.db_name)
        except Exception as e:
            logger.error('Error in database configuration file ', exc_info=e)
        if self.connect_to:
            g.connect_to = self.connect_to
            try:
                g.registry.servers.update(
                    operations.connect_to_server().json()
                )
                logger.debug(g.registry.servers)
                operations.connect_to_all_servers()
            except Exception as e:
                logger.error('Connecting to other servers failed ',
                             exc_info=e)
                shutdown()

    def run(self, production=None):
        """
        Run server in develop or in production mode
        :return:
        """
        logging.basicConfig(level=logging.INFO)
        if production:
            self.execute()
        else:
            with app.app_context():
                self.execute()
            app.run(
                host='127.0.0.1',
                port=int(self.serving_at_port),
                threaded=True
            )


def shutdown():
    """
    Log out from other servers and then shutdown
    :return:
    """
    operations.unregister_from_servers()
    g.db.close_connection()
    exit()


def signal_handler(signum, frame):
    """
    Handle registered signals
    :param signum:
    :param frame:
    :return:
    """
    logger.warning('Signal handler called with signal {}'.format(signum))
    shutdown()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
