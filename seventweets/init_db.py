import time
import pg8000


def init(database, server_name):
    db = pg8000.connect(user=server_name, database=database, host='localhost',
                        port=5432, password=None)
    c = db.cursor()
    c.execute('DROP TABLE IF EXISTS tweets;')
    c.execute('''
        CREATE TABLE tweets (
        id SERIAL PRIMARY KEY,
        name VARCHAR(20) NOT NULL,
        tweet TEXT,
        creation_time TEXT DEFAULT (timeofday()::TIMESTAMP),
        type VARCHAR(10) DEFAULT 'original'
        CHECK(type IN ('original', 're_tweet')),
        reference TEXT);
        ''')

    values = [(server_name, '1st tweet'),
              (server_name, '2nd tweet'),
              (server_name, '3rd tweet')]

    for i in range(0, 3):
        time.sleep(0.01)
        c.execute('INSERT INTO tweets (name,tweet) '
                  'VALUES (%s ,%s);', values[i])
    db.commit()
    c.close()
    db.close()
