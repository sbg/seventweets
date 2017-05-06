import abc
import logging
from flask import jsonify
from functools import wraps

logger = logging.getLogger(__name__)


class HttpException(Exception, metaclass=abc.ABCMeta):
    """
    Base exception for all HTTP related errors.
    """
    CODE = 0


class BadRequest(HttpException):
    CODE = 400


class Unauthorized(HttpException):
    CODE = 401


class Forbidden(HttpException):
    CODE = 403


class NotFound(HttpException):
    CODE = 404


class Conflict(HttpException):
    CODE = 409


class ServerError(HttpException):
    CODE = 500


class BadGateway(HttpException):
    CODE = 502


class ServiceUnavailable(HttpException):
    CODE = 503


def error_handler(f):
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
        except Exception as e:
            body = {
                'message': str(e),
                'code': 500,
            }
            logger.exception(body['message'])
            return jsonify(body), 500
    return wrapper
