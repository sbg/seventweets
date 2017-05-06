import pytest
from seventweets.exceptions import (
    error_handler, BadRequest, Unauthorized, Forbidden, NotFound, Conflict,
    ServerError, BadGateway, ServiceUnavailable,
)


class _CustomExc(Exception):
    pass


@pytest.mark.parametrize(
    ('code', 'exc', 'msg'),
    [
        (400, BadRequest, 'bad gateway'),
        (401, Unauthorized, 'unauthorized'),
        (403, Forbidden, 'forbidden'),
        (404, NotFound, 'not found'),
        (409, Conflict, 'conflict'),
        (500, ServerError, 'server error'),
        (502, BadGateway, 'bad gateway'),
        (503, ServiceUnavailable, 'unavailable'),
        (500, ValueError, 'value error'),
        (500, _CustomExc, 'custom exception'),
    ]
)
def test_except_handler_errors(app, code, exc, msg):
    @error_handler
    def foo():
        raise exc(msg)

    with app.app_context():
        resp, status_code = foo()
        assert status_code == code
        assert resp.json['message'] == msg


def test_exception_handler_success(app):
    @error_handler
    def foo():
        return 'response data', 200

    with app.app_context():
        resp, status_code = foo()
        assert status_code == 200
        assert resp == 'response data'
