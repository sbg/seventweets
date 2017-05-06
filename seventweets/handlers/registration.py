import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from seventweets.exceptions import (
    error_handler, BadRequest, NotFound, BadGateway
)
from seventweets.handlers.utils import ensure_bool
from seventweets import registry

logger = logging.getLogger(__name__)


register = Blueprint('register', __name__)


@register.route('/', methods=['GET'])
def list_registered():
    return jsonify([n.to_dict() for n in registry.get_all()])


@register.route('/', methods=['POST'])
@error_handler
def register_server():
    body = request.get_json(force=True)
    if body is None:
        raise BadRequest('No body is provided.')
    if 'name' not in body or 'address' not in body:
        raise BadRequest('Required fields for registration are: name, address')
    force_update = ensure_bool(request.args.get('force', None))
    registry.add(body['name'], body['address'], force_update)
    all_nodes = registry.get_all()
    all_nodes.append(
        registry.Node(
            current_app.config['ST_OWN_NAME'],
            current_app.config['ST_OWN_ADDRESS'],
            datetime.now()
        )
    )
    return jsonify([node.to_dict() for node in all_nodes]), 201


@register.route('/<string:name>', methods=['DELETE'])
@error_handler
def unregister_server(name):
    deleted = registry.delete(name)
    if deleted:
        return '', 204
    else:
        raise NotFound(f'Node with name {name} not found.')


@register.route('/join_network', methods=['POST'])
@error_handler
def join_network():
    body = request.get_json(force=True)
    if body is None:
        raise BadRequest('No body is provided.')
    if 'name' not in body or 'address' not in body:
        raise BadRequest(
            'Required fields for joining a network are: name, address '
            'of existing node'
        )

    node = registry.Node(body['name'], body['address'], None)
    try:
        network_nodes = node.client.register(
            {'name': current_app.config['ST_OWN_NAME'],
             'address': current_app.config['ST_OWN_ADDRESS']},
            force_update=True
        )

    # this is coming from the client so all possible errors are server errors,
    # no need for fine-tuned exception handling
    except Exception:
        raise BadGateway("The node you provided is unreachable.")
    registry.delete_all()
    [registry.add(node['name'], node['address']) for node in network_nodes if
     node['name'] != current_app.config['ST_OWN_NAME']]

    return jsonify('Node successfully joined network.')
