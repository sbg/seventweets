import logging
from datetime import datetime
from functools import partial
from concurrent.futures import ThreadPoolExecutor, wait
from seventweets.exceptions import NotFound, BadRequest
from seventweets.db import get_db, get_ops
from seventweets import registry
from typing import List


logger = logging.getLogger(__name__)


class Tweet:
    """
    Tweet model holding information about single tweet and providing operations
    on single tweet and multiple tweets (batch).
    """
    def __init__(self, id_, tweet, type_, created_at, modified_at,
                 reference=None):
        self.id = id_
        self.tweet = tweet
        self.created_at = created_at
        self.modified_at = modified_at
        self.type = type_
        self.reference = reference

    @property
    def content(self):
        if self.type == 'retweet':
            [server, id_] = self.reference.split('#')
            try:
                node = registry.get_node(server)
                original_tweet = node.client.get_tweet(id_)
                self.tweet = original_tweet['tweet']
            except Exception as e:
                pass
        return self.tweet

    def to_dict(self):
        """
        Converts tweet to dictionary. Optional fields may not exist in
        resulting dictionary.

        :return: Tweet represented as dictionary.
        """
        r = {
            'id': self.id,
            'type': self.type,
            'tweet': self.content,
            'created_at': self.created_at.isoformat('T') + 'Z',
            'modified_at': self.modified_at.isoformat('T') + 'Z',
        }
        if self.type == 'retweet':
            r['reference'] = self.reference
        return r

    @classmethod
    def from_dict(cls, tweet_dict):
        try:
            id_ = tweet_dict['id']
            tweet = tweet_dict['tweet']
            type_ = tweet_dict['type']
            created_at = datetime.strptime(
                tweet_dict['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            modified_at = datetime.strptime(
                tweet_dict['modified_at'], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            return cls(id_, tweet, type_, created_at, modified_at, None)
        except KeyError:
            raise ValueError("Invalid format of tweet dict provided.")


def get_all():
    """
    Returns list of all tweets.
    :rtype: [Tweet]
    """
    return [Tweet(*args) for args in get_db().do(get_ops().get_all_tweets)]


def by_id(id_):
    """
    Returns tweet with specified ID.
    :param int id_: ID of tweet to get.
    :return: Tweet with requested ID.
    :rtype: Tweet
    :raises NotFound: If tweet with provided ID was not found.
    """
    res = get_db().do(partial(get_ops().get_tweet, id_))
    if res is None:
        raise NotFound(f'Tweet with id: {id_} not found.')
    return Tweet(*res)


def create(content):
    """
    Creates new tweet with provided content.

    :param str content: Tweet content.
    :return: Created tweet.
    :rtype: Tweet
    """
    check_length(content)
    return Tweet(*get_db().do(partial(get_ops().insert_tweet, content)))


def modify(id_, content):
    """
    Modifies existing tweet with provided ID. New content will be set to
    whatever is provided.

    :param int id_: ID of tweet to modify.
    :param str content: New tweet content.
    :return: Modified tweet.
    :rtype: Tweet
    :raises NotFound: If tweet with provided ID was not found.
    """
    check_length(content)
    updated = get_db().do(partial(get_ops().modify_tweet, id_, content))
    if not updated:
        raise NotFound(f'Tweet for ID: {id_} not found.')
    return Tweet(*updated)


def delete(id_):
    """
    Removes tweet with provided ID from database.
    :param id_: ID of tweet to delete.
    :raises NotFound: If tweet with provided ID was not found.
    """
    deleted = get_db().do(partial(get_ops().delete_tweet, id_))
    if not deleted:
        raise NotFound(f'Tweet with ID: {id_} not found.')
    return deleted


def retweet(server, id_):
    """
    Creates retweet of original tweet.

    :param server: Server name that holds original tweet.
    :param id_: ID of tweet on original server.
    :return: Newly created tweet.
    :rtype: Tweet
    """
    return Tweet(*get_db().do(partial(get_ops().create_retweet, server, id_)))


def search(content: str=None,
           from_created: datetime=None,
           to_created: datetime=None,
           from_modified: datetime=None,
           to_modified: datetime=None,
           retweet: bool=None,
           all: bool=False) -> List[Tweet]:
    """
    Performs search on tweets and returns list of results.
    If no parameters are provided, this will yield same results as
    listing tweets.

    :param content: Content to search in tweet.
    :param from_created: Start time for tweet creation.
    :param to_created: End time for tweet creation.
    :param from_modified: Start time for tweet modification.
    :param to_modified: End time for tweet modification.
    :param retweet:
        Flag indication if retweet or original tweets should be searched.
    :param all:
        Flag indicating if all nodes should be searched or only this one.
    :return: Result searching tweets.
    :rtype: [Tweet]
    """
    search_func = partial(get_ops().search_tweets, content, from_created,
                          to_created, from_modified, to_modified, retweet)
    res = [Tweet(*args) for args in get_db().do(search_func)]
    if all:
        others_res = search_others(content, from_created, to_created,
                                   from_modified, to_modified, retweet)
        res.extend(others_res)
    return res


def search_others(content: str=None,
                  from_created: datetime=None,
                  to_created: datetime=None,
                  from_modified: datetime=None,
                  to_modified: datetime=None,
                  retweet: bool=None) -> List[Tweet]:
    tp = ThreadPoolExecutor(max_workers=5)
    futures = []
    results = []

    for n in registry.get_all():
        futures.append(
            tp.submit(n.client.search, content, from_created, to_created,
                      from_modified, to_modified, retweet, False)
        )

    wait(futures)
    for future in futures:
        try:
            res = future.result()
            results.extend([Tweet.from_dict(r) for r in res])
        except Exception:
            logger.warning('Unable to get results from a server.')

    return results


def count(type_: str=None):
    """
    Returns number of tweets in database. If `separate` is True, two values
    are returned. First is number of original tweets and second is number of
    retweets.

    If `separate` if False (default) only one number is returned.

    :param type_:
        Type of tweets to count. Valid values are 'original' and 'retweet'.
    :return:
    """
    return get_db().do(partial(get_ops().count_tweets, type_))


def check_length(tweet):
    """
    Verifies if provided tweet content is less then 140 characters.

    :param str tweet: Tweet content to check.
    :raises BadRequest: If tweet content is longer then 140 characters.
    """
    if len(tweet) > 140:
        raise BadRequest('Tweet length exceeds 140 characters.')
