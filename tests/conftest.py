import pytest

from tests.postgres import TestPostgresql
from seventweets.models import Registry


class Database:
    def __init__(self, my_name, db_name):
        self.instance = instance = TestPostgresql()
        self.db_con = instance.conn
        self.my_name = my_name
        self.db_name = db_name

    def query_execute(self, query, args=()):
        db = self.db_con
        cur = db.cursor()
        cur.execute(query, args)
        result = cur.fetchall()
        db.commit()
        cur.close()
        return result

    def stop(self):
        self.instance.stop()


@pytest.fixture(scope='session')
def g():
    from seventweets.config import g
    from tests.mocks import Client

    g.get_client = lambda **kwargs: Client
    g.my_name = 'prvi'
    g.port = 5000
    g.db_name = 'prviserver'
    g.my_address = '127.0.0.1:5000'
    g.registry = Registry(name=g.my_name, address=g.my_address)
    g.db = Database(my_name=g.my_name, db_name=g.db_name)
    g.connect_to = '127.0.0.1:5001'
    g.registry.servers.update(
        {'drugi': '127.0.0.1:5001',
         'treci': '127.0.0.1:5002'}
    )
    yield g
    g.db.stop()


@pytest.fixture(scope='session')
def app():
    from seventweets.server import app
    return app
