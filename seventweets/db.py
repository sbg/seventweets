import logging

from seventweets.config import g

logger = logging.getLogger(__name__)


def insert_tweet(tweet):
    """
    Inserts new tweet and returns id of the created row
    :param tweet: tweet content
    :return: id of the tweet
    """
    query = 'INSERT INTO tweets (name,tweet) VALUES (%s,%s) RETURNING id'
    id = g.db.query_execute(query, (g.my_name, tweet))[0][0]
    return id


def delete_tweet(id):
    """
    Deletes tweet with supplied id
    :param id: id of the tweet to be deleted
    :return: 1 if tweet with that id exists else 0
    """
    query1 = 'SELECT COUNT(id) FROM tweets WHERE id = %s'
    id_exists = g.db.query_execute(query1, (id,))[0][0]
    if id_exists:
        query2 = 'DELETE FROM tweets WHERE id = %s RETURNING *'
        g.db.query_execute(query2, (id,))
    return id_exists


def modify_tweet(tweet, id):
    """
    Updates tweet content with supplied id
    :param tweet: content to be replaced
    :param id: id of the tweet to modify
    :return: 1 if tweet with that id exists else 0
    """
    query1 = 'SELECT COUNT(id) FROM tweets WHERE id = %s'
    id_exists = g.db.query_execute(query1, (id,))[0][0]
    if id_exists:
        query2 = 'UPDATE tweets SET tweet= %s WHERE id = %s RETURNING *'
        g.db.query_execute(query2, (tweet, id))
    return id_exists


def create_re_tweet(name, ref_id):
    """
    Creates new re-tweet
    :param name: Server name that holds original tweet
    :param ref_id: id of the tweet which is re-tweeted
    :return: id of the created row
    """
    query = '''INSERT INTO tweets (name, type, reference)
               VALUES (%s, %s, %s) RETURNING id'''
    id = g.db.query_execute(
        query,
        (g.my_name, 're_tweet', '{}#{}'.format(name, ref_id))
    )[0][0]
    return id


def get_all_tweets():
    """
    Returns all tweets from this db
    :return: all tweets as rows
    """
    query = '''SELECT id, name, tweet, creation_time, type, reference
               FROM tweets'''
    return g.db.query_execute(query)


def get_tweet_by_id(id):
    """
    Returns tweet with supplied id
    :param id: id of the tweet
    :return: tweet as row
    """
    query = '''SELECT id,name,tweet,creation_time,type,reference
               FROM tweets WHERE id = %s'''
    return g.db.query_execute(query, (id,))


def get_retweets_refined(args, start_time):
    """
    Acquires query for searching re-tweets with start_time and executes query
    :param args: Object that holds search params
    :param start_time: offset when search requires paging
    :return: result re-tweet rows
    """
    query, params = args.query_creator(retweet=True, start_time=start_time)
    print(query)
    return g.db.query_execute(query, tuple(params))


def search_tweets(args, retweet):
    """
    Acquires query for searching tweets and re-tweets and executes query
    :param args: Object that holds search params
    :param retweet: boolean that determines type
    :return: tweets as rows
    """
    if retweet:
        query, params = args.query_creator(retweet=True)
    else:
        query, params = args.query_creator(retweet=False)
    return g.db.query_execute(query, tuple(params))
