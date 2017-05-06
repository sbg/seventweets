import pytest

from seventweets.auth import auth
from seventweets.exceptions import Unauthorized


@pytest.mark.parametrize(
    ('server_token', 'client_token'),
    [
        ('token', 'different token'),
        (None, 'client token'),
        ('server token', None),
        (None, None),
    ],
    ids=('different', 'only-client', 'only-server', 'none')
)
def test_auth_fail(app, server_token, client_token):
    app.config['ST_API_TOKEN'] = server_token

    @auth
    def foo():
        return 'content'

    with app.test_request_context(headers={'X-Api-Token': client_token}):
        with pytest.raises(Unauthorized):
            foo()


def test_auth_success(app):
    app.config['ST_API_TOKEN'] = 'known_token'

    @auth
    def foo():
        return 'content'

    with app.test_request_context(headers={'X-Api-Token': 'known_token'}):
        resp = foo()
        assert resp == 'content'
