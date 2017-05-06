id = 2


def upgrade(cursor):
    # TODO: Should reference be unique? Does it make sense to retweet
    # same tweet twice?
    cursor.execute('''
        ALTER TABLE tweets
            ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT now(),
            ADD COLUMN modified_at TIMESTAMP NOT NULL DEFAULT now(),
            ADD COLUMN type VARCHAR(32) DEFAULT 'original'
                       CHECK(type IN ('original', 'retweet')),
            ADD COLUMN reference TEXT;
    ''')


def downgrade(cursor):
    cursor.execute('''
        ALTER TABLE tweets
            DROP COLUMN created_at,
            DROP COLUMN modified_at,
            DROP COLUMN type,
            DROP COLUMN reference;
    ''')
