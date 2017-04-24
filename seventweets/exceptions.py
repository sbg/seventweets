from flask import jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class HttpException(Exception):
    CODE = 0


class BadRequest(HttpException):
    CODE = 400


class NotFound(HttpException):
    CODE = 404


class Forbidden(HttpException):
    CODE = 403


def except_handler(f):
    """
    Handles exceptions caught in http layer (server.py)
    :param f: wrapped function
    :return: function or appropriate exception message
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HttpException as e:
            body = {
                'message': str(e),
                'code': e.CODE,
            }
            logger.warning(body['message'])
            return jsonify(body), e.CODE
        except TypeError:
            body = {
                'message': 'bad request',
                'code': 400,
            }
            logger.exception(body['message'])
            return jsonify(body), 400
        except KeyError:
            body = {
                'message': 'bad request json does not have required fields',
                'code': 400,
            }
            logger.exception(body['message'])
            return jsonify(body), 400
        except Exception as e:
            body = {
                'message': str(e),
                'code': 500,
            }
            logger.exception(body['message'])
            return jsonify(body), 500
    return wrapper
