from flask import Blueprint, current_app, jsonify
from seventweets.exceptions import error_handler
from seventweets import tweet

base = Blueprint('base', __name__)


@base.route('/')
@error_handler
def index():
    original = tweet.count('original')
    retweets = tweet.count('retweet')
    return jsonify({
        'name': current_app.config['ST_OWN_NAME'],
        'address': current_app.config['ST_OWN_ADDRESS'],
        'stats': {
            'original': original,
            'retweets': retweets,
            'total': original + retweets,
        }
    })
