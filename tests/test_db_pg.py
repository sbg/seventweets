import pytest
from unittest.mock import MagicMock, PropertyMock
from seventweets import db


def assert_query(cursor, columns, params, table, type_='SELECT',
                 more_query=None):
    assert cursor.execute.called
    executed_query = cursor.execute.call_args[0][0]
    used_params = None
    if len(cursor.execute.call_args[0]) > 1:
        used_params = cursor.execute.call_args[0][1] or None
    assert columns in executed_query
    if params:
        for p in params:
            assert p in used_params
    assert table in executed_query
    assert type_ in executed_query
    more_query = more_query or []
    for mq in more_query:
        assert mq in executed_query


def assert_fetch_single(cursor):
    assert cursor.fetchone.called is True


def assert_fetch_all(cursor):
    assert cursor.fetchall.called is True


def test_get_all_tweets():
    cursor = MagicMock()
    db.get_ops().get_all_tweets(cursor)
    assert_query(cursor, db.TWEET_COLUMN_ORDER, None, 'tweets')
    assert_fetch_all(cursor)


def test_get_tweet():
    cursor = MagicMock()
    db.get_ops().get_tweet(33, cursor)
    assert_query(cursor, db.TWEET_COLUMN_ORDER, (33,), 'tweets')
    assert_fetch_single(cursor)


def test_insert_tweet():
    cursor = MagicMock()
    content = 'some interesting tweet'
    db.get_ops().insert_tweet(content, cursor)
    assert_query(cursor, db.TWEET_COLUMN_ORDER, (content,), 'tweets',
                 'INSERT')
    assert_fetch_single(cursor)


def test_modify_tweet():
    cursor = MagicMock()
    id_ = 42
    content = 'new tweet content'
    db.get_ops().modify_tweet(id_, content, cursor)
    assert_query(cursor, db.TWEET_COLUMN_ORDER, (content, id_), 'tweets',
                 'UPDATE', 'modified_at')
    assert_fetch_single(cursor)


def test_delete_tweet():
    cursor = MagicMock()
    cursor.rowcount = 1
    id_ = 43
    res = db.get_ops().delete_tweet(id_, cursor)
    assert res is True
    assert_query(cursor, '', (id_,), 'tweets', 'DELETE')


def test_create_retweet():
    cursor = MagicMock()
    server = 'some_server',
    ref = 44
    db.get_ops().create_retweet(server, ref, cursor)
    assert_query(cursor, db.TWEET_COLUMN_ORDER,
                 ('retweet', f'{server}#{ref}'), 'tweets', 'INSERT')


@pytest.mark.parametrize(
    ('params', 'expected_in_query', 'expected_in_params'),
    [
        ({'content': 'foo'}, ('tweet',), ('%foo%',)),
        ({'from_created': 'foo'}, ('created_at',), ('foo',)),
        ({'to_created': 'foo'}, ('created_at',), ('foo',)),
        ({'from_modified': 'foo'}, ('modified_at',), ('foo',)),
        ({'to_modified': 'foo'}, ('modified_at',), ('foo',)),
        ({'retweet': True}, ('type',), ('retweet',)),
        (
            {'content': 'foo', 'retweet': True},
            ('tweet', 'type',),
            ('%foo%', 'retweet',)
        ),
        (
            {'retweet': True, 'from_created': 'bar'},
            ('created_at', 'type',),
            ('bar', 'retweet',)
        ),
    ]
)
def test_search_tweets(params, expected_in_query, expected_in_params):
    all_args = {'content', 'from_created', 'to_created', 'from_modified',
                'to_modified', 'retweet'}
    for arg in all_args:
        if arg not in params:
            params[arg] = None

    cursor = MagicMock()
    params['cursor'] = cursor

    db.get_ops().search_tweets(**params)
    assert_query(cursor, db.TWEET_COLUMN_ORDER, expected_in_params, 'tweets',
                 more_query=expected_in_query)
    assert_fetch_all(cursor)


@pytest.mark.parametrize(
    'type', ('original', 'retweet', None),
)
def test_count_tweets(type):
    cursor = MagicMock()
    db.get_ops().count_tweets(type, cursor)
    assert_query(cursor, '', tuple(filter(None, [type])), 'tweets')
    assert_fetch_single(cursor)


def test_get_all_nodes():
    cursor = MagicMock()
    db.get_ops().get_all_nodes(cursor)
    assert_query(cursor, db.NODE_COLUMN_ORDER, None, 'nodes')
    assert_fetch_all(cursor)


def test_insert_node():
    cursor = MagicMock()
    name = 'node_name'
    address = 'node address'
    db.get_ops().insert_node(name, address, cursor)
    assert_query(cursor, db.NODE_COLUMN_ORDER, (name, address), 'nodes',
                 'INSERT')
    assert_fetch_single(cursor)


def test_get_node():
    cursor = MagicMock()
    db.get_ops().get_node('node', cursor)
    assert_query(cursor, db.NODE_COLUMN_ORDER, ('node',), 'nodes')
    assert_fetch_single(cursor)


def test_update_node():
    cursor = MagicMock()
    name = 'node name'
    address = 'node address'
    db.get_ops().update_node(name, address, cursor)
    assert_query(cursor, db.NODE_COLUMN_ORDER, (name, address), 'nodes',
                 'UPDATE')
    assert_fetch_single(cursor)


def test_delete_node():
    cursor = MagicMock()
    cursor.rowcount = 1
    name = 'node name'
    res = db.get_ops().delete_node(name, cursor)
    assert res is True
    assert_query(cursor, '', (name,), 'nodes', 'DELETE')
