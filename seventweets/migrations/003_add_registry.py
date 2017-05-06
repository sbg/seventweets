id = 3


def upgrade(cursor):
    cursor.execute('''
        CREATE TABLE nodes (
            name VARCHAR(32) NOT NULL PRIMARY KEY,
            address VARCHAR(128) NOT NULL,
            last_checked_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    ''')


def downgrade(cursor):
    cursor.execute('''
        DROP table nodes;
    ''')
