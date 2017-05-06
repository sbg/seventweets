id = 1


def upgrade(cursor):
    cursor.execute('''
        CREATE TABLE tweets (
            id SERIAL PRIMARY KEY,
            tweet VARCHAR(140)
        );
    ''')


def downgrade(cursor):
    cursor.execute('''
        DROP TABLE tweets;
    ''')
