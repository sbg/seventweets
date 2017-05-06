import logging
from flask import Blueprint, request, jsonify
from seventweets.exceptions import error_handler, BadRequest
from seventweets.handlers.utils import ensure_dt, ensure_bool
from seventweets import tweet
from seventweets.auth import auth


tweets = Blueprint('tweets', __name__)
logger = logging.getLogger(__name__)


@tweets.route('/', methods=['GET'])
@error_handler
def get_all():
    """
    Returns list of all tweets from this server.
    """
    return jsonify([t.to_dict() for t in tweet.get_all()])


@tweets.route('/<int:tweet_id>', methods=['GET'])
@error_handler
def get_single(tweet_id):
    """
    Returns single tweet by ID.
    :param tweet_id: ID of the tweet to get.
    """
    return jsonify(tweet.by_id(tweet_id).to_dict())


@tweets.route('/', methods=['POST'])
@error_handler
def create_tweet():
    """
    Creates new tweet and returns its JSON representation.
    """
    body = request.get_json(force=True)
    if 'tweet' not in body:
        raise BadRequest('Invalid body: no "tweet" key in body.')
    content = body['tweet']
    new_tweet = tweet.create(content)
    return jsonify(new_tweet.to_dict()), 201


@tweets.route('/<int:tweet_id>', methods=['PUT'])
@error_handler
def modify(tweet_id):
    body = request.get_json(force=True)
    if 'tweet' not in body:
        raise BadRequest('Invalid body: no "tweet" key in body.')
    content = body['tweet']
    return jsonify(tweet.modify(tweet_id, content).to_dict())


@tweets.route('/<int:tweet_id>', methods=['DELETE'])
@error_handler
@auth
def delete(tweet_id):
    """
    Deletes tweet with provided ID.

    :param tweet_id: ID of the tweet to delete.
    """
    tweet.delete(tweet_id)
    return '', 204


@tweets.route('/retweet', methods=['POST'])
@error_handler
def retweet():
    """
    Creates retweet on this server that references tweet on provided server.
    """
    body = request.get_json(force=True)
    if 'server' not in body or 'id' not in body:
        raise BadRequest('Missing wither "server" or "id" from body.')
    return jsonify(tweet.retweet(body['server'], body['id']).to_dict())


@tweets.route('/search', methods=['GET'])
@error_handler
def search_single():
    """
    Performs search in database for tweets in this node only.
    """
    content = request.args.get('content', None) or None
    created_from = ensure_dt(request.args.get('created_from', None) or None)
    created_to = ensure_dt(request.args.get('created_to', None) or None)
    modified_from = ensure_dt(request.args.get('modified_from', None) or None)
    modified_to = ensure_dt(request.args.get('modified_to', None) or None)
    retweets = ensure_bool(request.args.get('retweets', None) or None)
    all = ensure_bool(request.args.get('all', None) or None)

    results = tweet.search(content, created_from, created_to,
                           modified_from, modified_to, retweets, all)
    return jsonify([t.to_dict() for t in results])
