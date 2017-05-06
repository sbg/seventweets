import logging
from datetime import datetime
from collections import namedtuple
from typing import Iterable, Optional, List, Dict

import itertools

from seventweets import db
from seventweets.db import (
    TwResp, NdResp,
    TWEET_COLUMN_ORDER, NODE_COLUMN_ORDER,
)

logger = logging.getLogger(__name__)

Tweet = namedtuple('Tweet', TWEET_COLUMN_ORDER)
Node = namedtuple('Node', NODE_COLUMN_ORDER)


class Database:
    """
    In-memory storage for :class:`Operations`.
    """

    def __init__(self):
        self.tweets = list()  # type: List[Tweet]
        self.nodes = dict()  # type: Dict[str, Node]
        self.counter = itertools.count()

    def test_connection(self):
        pass

    def cleanup(self):
        pass

    def close(self):
        pass

    def do(self, fn):
        """
        Executes provided fn and gives it a storage to work with.

        :param fn:
            Function to execute.
            It has to accept one argument, the :class:`Database` instance.
        :return: Whatever `fn` returns
        """
        return fn(self)


class Operations(db.Operations):

    ################################################
    # Tweet related methods
    ################################################

    @staticmethod
    def insert_tweet(tweet: str, storage: Database):
        now = datetime.now()
        new_tweet = Tweet(
            id=next(storage.counter), tweet=tweet, type='original',
            created_at=now, modified_at=now, reference=''
        )
        storage.tweets.append(new_tweet)
        return new_tweet

    @staticmethod
    def search_tweets(content: Optional[str], from_created: Optional[datetime],
                      to_created: Optional[datetime],
                      from_modified: Optional[datetime],
                      to_modified: Optional[datetime], retweet: Optional[bool],
                      storage: Database) -> Iterable[TwResp]:
        return [
            tweet
            for tweet in storage.tweets if (
                (retweet is None or (tweet.type == 'retweet') == retweet) and
                (to_modified is None or tweet.modified_at <= to_modified) and
                (from_modified is None or tweet.modified_at >= from_modified) and
                (to_created is None or tweet.created_at <= to_created) and
                (from_modified is None or tweet.created_at >= from_created) and
                (content is None or content.lower() in tweet.content.lower())
            )
        ]

    @staticmethod
    def modify_tweet(id_: int, new_content: str, storage: Database) -> TwResp:
        tweet = Operations.get_tweet(id_, storage)  # type: Tweet
        assert tweet.type == 'original'
        new_tweet = Tweet(
            id=tweet.id, tweet=new_content, type=tweet.type,
            created_at=tweet.created_at,
            modified_at=tweet.modified_at,
            reference=tweet.reference
        )
        storage.tweets.remove(tweet)
        storage.tweets.append(new_tweet)
        return new_tweet

    @staticmethod
    def create_retweet(server: str, ref: str, storage: Database) -> TwResp:
        now = datetime.now()
        new_tweet = Tweet(
            id=next(storage.counter), tweet='', type='retweet',
            created_at=now, modified_at=now, reference=f'{server}#{ref}'
        )
        storage.tweets.append(new_tweet)
        return new_tweet

    @staticmethod
    def get_tweet(id_: int, storage: Database):
        for tweet in storage.tweets:
            if tweet.id == id_:
                return tweet
        else:
            raise KeyError(f'Tweet with id={id_} not found.')

    @staticmethod
    def count_tweets(type_: str, storage: Database) -> int:
        return len([
            tweet
            for tweet in storage.tweets
            if tweet.type == type_
        ])

    @staticmethod
    def get_all_tweets(storage: Database):
        return storage.tweets

    @staticmethod
    def delete_tweet(id_: int, storage: Database) -> bool:
        try:
            storage.tweets.remove(Operations.get_tweet(id_, storage))
            return True
        except KeyError:
            return False

    ################################################
    # Node related methods
    ################################################

    @staticmethod
    def update_node(name: str, address: str, storage: Database) -> NdResp:
        assert name in storage.nodes
        new_node = Node(name=name, address=address,
                        last_checked_at=datetime.now())
        storage.nodes[name] = new_node
        return new_node

    @staticmethod
    def delete_node(name: str, storage: Database) -> bool:
        try:
            del storage.nodes[name]
            return True
        except KeyError:
            return False

    @staticmethod
    def delete_all_nodes(storage: Database) -> bool:
        storage.nodes = dict()

    @staticmethod
    def get_all_nodes(storage: Database) -> Iterable[NdResp]:
        return list(storage.nodes.values())

    @staticmethod
    def insert_node(name: str, address: str, storage: Database) -> NdResp:
        assert name not in storage.nodes
        new_node = Node(name=name, address=address,
                        last_checked_at=datetime.now())
        storage.nodes[name] = new_node
        return new_node

    @staticmethod
    def get_node(name: str, storage: Database) -> NdResp:
        return storage.nodes[name]
