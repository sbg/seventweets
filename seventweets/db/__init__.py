import os
import abc
import logging
from importlib import import_module
from seventweets import config

import flask
from datetime import datetime
from typing import TypeVar, Tuple, Iterable, Optional

# type for type hinting
_T = TypeVar('_T')
TwResp = Tuple[int, str, str, datetime, datetime, str]
NdResp = Tuple[str, str, datetime]


logger = logging.getLogger(__name__)


# This is order in which columns will be selected from database.
# Tweet and Node models will be interested in this order to read it properly.
TWEET_COLUMN_ORDER = 'id, tweet, type, created_at, modified_at, reference'
NODE_COLUMN_ORDER = 'name, address, last_checked_at'


class Operations(metaclass=abc.ABCMeta):

    ################################################
    # Tweet related methods
    ################################################

    @staticmethod
    @abc.abstractmethod
    def get_all_tweets(cursor):
        """
        Returns all tweets from database.

        :param cursor: Database cursor.
        :return: All tweets from database.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def get_tweet(id_: int, cursor):
        """
        Returns single tweet from database.

        :param id_: ID of tweet to get.
        :param cursor: Database cursor.
        :return: Tweet with provided ID.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def insert_tweet(tweet: str, cursor):
        """
        Inserts new tweet and returns id of the created row

        :param tweet: Content of the tweet to add.
        :param cursor: Database cursor.
        :return: ID of the tweet that was created.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def modify_tweet(id_: int, new_content: str, cursor) -> TwResp:
        """
        Updates tweet content.

        :param id_: ID of tweet to update.
        :param new_content: New tweet content.
        :param cursor: Database cursor.
        :return:
            Tweet that was update, if tweet with provided ID was found, None
            otherwise.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def delete_tweet(id_: int, cursor) -> bool:
        """
        Deletes tweet with provided ID from database.

        :param id_: ID of tweet to delete.
        :param cursor: Database cursor.
        :return:
            Boolean indicating if tweet with ID was deleted (False if tweet
            does not exist).
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def create_retweet(server: str, ref: str, cursor) -> TwResp:
        """
        Creates retweet in database that references server and tweet ID
        provided in parameters.

        :param server: Server name of original tweet.
        :param ref: Tweet reference (ID) on original server.
        :param cursor: Database cursor.
        :return: Newly created tweet.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def search_tweets(content: Optional[str], from_created: Optional[datetime],
                      to_created: Optional[datetime],
                      from_modified: Optional[datetime],
                      to_modified: Optional[datetime],
                      retweet: Optional[bool],
                      cursor) -> Iterable[TwResp]:
        """
        :param content: Content to search in tweet.
        :param from_created: Start time for tweet creation.
        :param to_created: End time for tweet creation.
        :param from_modified:
            Start time for tweet modification.
        :param to_modified:
            End time for tweet modification.
        :param retweet:
            Flag indication if retweet or original tweets should be searched.
        :param cursor: Database cursor.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def count_tweets(type_: str, cursor) -> int:
        """
        Returns number of tweets of specified type.

        :param type_: Type of tweet to count.
        :param cursor: Database cursor.
        """
        raise NotImplementedError()

    ################################################
    # Node related methods
    ################################################

    @staticmethod
    @abc.abstractmethod
    def get_all_nodes(cursor) -> Iterable[NdResp]:
        """
        :param cursor: Database cursor.
        :return: All nodes from database.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def insert_node(name: str, address: str, cursor) -> NdResp:
        """
        Inserts new nodes to database.

        :param name: Name of new node.
        :param address: Address of new node.
        :param cursor: Database cursor.
        :return: Node that was inserted.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def get_node(name: str, cursor) -> NdResp:
        """
        :param name: Name of the node to get.
        :param cursor: Database cursor.
        :return: Node with provided name.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def update_node(name: str, address: str, cursor) -> NdResp:
        """
        Updates existing node.

        :param name: Name of the node to update.
        :param address: New address to set for the node.
        :param cursor: Database cursor.
        :return: Node that was updated.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def delete_node(name: str, cursor) -> bool:
        """
        Deletes node from the database.

        :param name: Name of the node to delete.
        :param cursor: Database cursor.
        :return:
            Flag indicating if node was deleted or not. It is possible that
            node was not deleted if it was not found.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def delete_all_nodes(cursor) -> bool:
        """
        Deletes all nodes from the database.
        Only used when joining a network for updating the stale node list.

        :param cursor: Database cursor.
        :return:
            Flag indicating if nodes were deleted or not. It is possible that
            nodes weren't deleted if the list was previously empty.
        """
        raise NotImplementedError()


default_backend = os.getenv('ST_DB_BACKEND', 'pg')


def get_db(backend=default_backend):
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    backend_module = import_module(f'seventweets.db.backends.{backend}')
    return backend_module.Database()


def get_ops(backend=default_backend) -> Operations:
    backend_module = import_module(f'seventweets.db.backends.{backend}')
    return backend_module.Operations
