import logging

from seventweets import operations
from seventweets.exceptions import except_handler
from flask import Blueprint, request, jsonify, Response
from seventweets.models import QueryArgs

from seventweets import db

tweets_blueprint = Blueprint('tweets', __name__)
logger = logging.getLogger(__name__)


@tweets_blueprint.route('/retweet', methods=['POST'])
@except_handler
def create_re_tweet():
    """
    Handles request for creation of re-tweet
    :return: Response with id of created re-tweet
    """
    name = request.get_json()['name']
    id = request.get_json()['id']
    result = db.create_re_tweet(name=name, ref_id=id)
    return jsonify({'status': 'Re-tweet saved', 'id': str(result)}), 201


@tweets_blueprint.route('/tweets', methods=['POST'])
@except_handler
def create_tweet():
    """
    Handles request for creation of tweet
    :return: Response with id of created tweet
    """
    tweet = request.get_json()['tweet']
    id = db.insert_tweet(tweet)
    return jsonify({'message': 'Creation complete', 'id': id}), 201


@tweets_blueprint.route('/tweets/<int:id>', methods=['DELETE'])
@except_handler
def delete_tweet(id):
    """
    Handles request for tweet deletion
    :param id: id of the tweet
    :return: Response with status
    """
    operations.delete_tweet(id)
    return Response(status=204, headers={'message': 'Tweet deleted'})


@tweets_blueprint.route('/tweets/<int:id>', methods=['PUT'])
@except_handler
def update_tweet(id):
    """
    Handles request for update of tweet content
    :param id: id of the tweet
    :return: Response with message
    """
    tweet = request.get_json()['tweet']
    operations.modify_tweet(tweet=tweet, id=id)
    return jsonify({'message': 'Update complete'}), 201


@tweets_blueprint.route('/tweets/<int:id>', methods=['GET'])
@except_handler
def get_tweet(id):
    """
    Handles get request for specific tweet
    :param id: id of the tweet
    :return: Response with acquired tweet
    """
    result = operations.get_tweet(id)
    return jsonify(result)


@tweets_blueprint.route('/tweets', methods=['GET'])
@except_handler
def get_tweets():
    """
    Handles get request for all tweets on this server
    :return: Response with acquired tweets
    """
    result = operations.get_tweets()
    return jsonify(result)


@tweets_blueprint.route('/search', methods=['GET'])
@except_handler
def search_all():
    """
    Handles search request and makes QueryArgs object from params.
    Search is spread through all servers.
    :return: Response with acquired tweets and creation time of the last tweet
    in list if paging is required else 0
    """
    args = QueryArgs(
        content=request.args.get('content'),
        name=request.args.get('name'),
        from_time=request.args.get('from_time'),
        to_time=request.args.get('to_time'),
        per_page=request.args.get('per_page'),
        last_creation_time=request.args.get('last_creation_time')
    )
    result = operations.find_tweets(args)
    return jsonify({'items': result[0], 'last_creation_time': result[1]})


@tweets_blueprint.route('/search_me', methods=['GET'])
@except_handler
def search_me():
    """
    Handles search request and makes QueryArgs object from params.
    Search is done only on this server.
    :return: Response with acquired tweets
    """
    args = QueryArgs(
        content=request.args.get('content'),
        name=request.args.get('name'),
        from_time=request.args.get('from_time'),
        to_time=request.args.get('to_time'),
        per_page=request.args.get('per_page'),
        last_creation_time=request.args.get('last_creation_time')
    )
    result = operations.examine_tweets_from_this_server(args)

    return jsonify(result)
