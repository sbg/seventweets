import logging
from functools import partial
from seventweets import config
from seventweets.db import get_db, get_ops
from seventweets.client import Client
from seventweets.exceptions import Conflict
from typing import List


logger = logging.getLogger(__name__)


class Node:
    """
    Node represents remote instance of seventweets service.
    """
    def __init__(self, name, address, last_checked_at):
        self.name = name
        self.address = address
        self.last_checked_at = last_checked_at
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = Client(self.address,
                                  cleanup_callback=partial(delete, self.name))
        return self._client

    def to_dict(self):
        return {
            'name': self.name,
            'address': self.address,
        }


def get_node(name: str) -> Node:
    """
    Returns list of all nodes.
    """
    return Node(*get_db().do(partial(get_ops().get_node, name)))


def get_all(db=None) -> List[Node]:
    if not db:
        db = get_db()
    """
    Returns list of all nodes.
    """
    return [Node(*args) for args in db.do(get_ops().get_all_nodes)]


def add(name: str, address: str, update: bool=False) -> Node:
    """
    Adds new node to list of nodes.

    :param name: Name of the node.
    :param address: Address of the node.
    :param update:
        Flag indicating if update of existing node should be done if node is
        already registered.
    :return: Newly created node.
    :raises Conflict:
        If node with same name already exists and update is False.
    """
    found = get_db().do(partial(get_ops().get_node, name))
    if found:
        if not update:
            raise Conflict('Node with same name already registered.')
        else:
            return Node(*get_db().do(
                partial(get_ops().update_node, name, address)
            ))
    return Node(*get_db().do(partial(get_ops().insert_node, name, address)))


def delete(name: str) -> bool:
    """
    Deletes node from list of nodes.

    :param name: Name of node to delete.
    :return:
        Flag indicating if node was deleted. That might be false if node was
        not found.
    """
    return get_db().do(partial(get_ops().delete_node, name))


def delete_all() -> bool:
    """
    Deletes all nodes from list of nodes.

    :return:
        Flag indicating if nodes were deleted. That might be false if the
        list was empty previously.
    """
    return get_db().do(get_ops().delete_all_nodes)


def unregister_all(db):
    """
    Unregisters this node from all stored nodes and deletes them from
    the database.
    """
    logging.info("Leaving network mesh...")
    try:
        [node.client.unregister(config.ST_OWN_NAME) for node in get_all(db)]
    # only server errors are possible, ignore them since we're shutting down
    except Exception:
        pass
