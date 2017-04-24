import logging

from seventweets.config import g
from flask import Blueprint, request, jsonify

from seventweets.exceptions import except_handler

register_blueprint = Blueprint('register', __name__)
logger = logging.getLogger(__name__)


@register_blueprint.route('/register', methods=['POST'])
@except_handler
def register():
    """
    Handles register request
    :return: servers dict
    """
    address = '{}:{}'.format(request.remote_addr, request.get_json()['port'])
    name = request.get_json()['name']
    response = g.registry.register(name=name, address=address)
    logger.debug('registered: {}'.format(g.registry.servers[name]))
    return response


@register_blueprint.route('/unregister/<string:name>', methods=['DELETE'])
@except_handler
def unregister(name):
    """
    Handles unregister request
    :param name: Server which to remove from servers dict
    :return: json with message
    """
    ip = request.remote_addr
    g.registry.unregister(name, ip)
    logger.debug('unregistered: {}'.format(name))
    return jsonify({'status': 'removal complete'})
