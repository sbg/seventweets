import testing.postgresql
import pg8000


class TestPostgresql(object):
    def __init__(self):
        # start postgresql server
        self.pgsql = testing.postgresql.Postgresql()

        # connect to postgresql (w/ pg8000)
        self.conn = pg8000.connect(**self.pgsql.dsn())

        self.create_tweets_table()

    def create_tweets_table(self):
        query = '''
                    CREATE TABLE tweets (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(20) NOT NULL,
                    tweet TEXT,
                    creation_time TEXT DEFAULT (timeofday()::TIMESTAMP),
                    type VARCHAR(10) DEFAULT 'original'
                    CHECK(type IN ('original', 're_tweet')),
                    reference TEXT);
                    '''
        cursor = self.conn.cursor()
        cursor.execute(query, ())
        self.conn.commit()
        cursor.close()

    def stop(self):
        self.pgsql.terminate()
