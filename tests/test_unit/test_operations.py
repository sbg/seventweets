from seventweets import operations
from seventweets.models import QueryArgs
from tests.test_api.test_endpoints import fill_db_prvi_with_data


def test_connect_to_server(g):
    assert operations.connect_to_server().json()['status'] == 'ok'


def test_connect_to_all_servers(g):
    assert g.my_name == 'prvi'
    assert g.port == 5000
    operations.connect_to_all_servers()


def test_unregister_from_servers(g):
    assert g.my_name == 'prvi'
    assert g.port == 5000
    operations.unregister_from_servers()


def test_append_available(g, client):

    fill_db_prvi_with_data(g, client)

    args = QueryArgs(
        content=None,
        name=None,
        from_time=None,
        to_time=None,
        per_page=None,
        last_creation_time=None
    )
    assert operations.append_available(
        results=[],
        args=args,
        twt_countdown=0,
        start_time='0'
    ) == (False, 0, 0)

    args = QueryArgs(
        content='kkkkkk',
        name=None,
        from_time=None,
        to_time=None,
        per_page=None,
        last_creation_time=None
    )
    boolean, _, twt_countdown = operations.append_available(
        results=[],
        args=args,
        twt_countdown=2,
        start_time='0'
    )
    assert (boolean, twt_countdown) == (True, 2)

    args = QueryArgs(
        content='day',
        name=None,
        from_time=None,
        to_time=None,
        per_page=None,
        last_creation_time=None
    )
    boolean, _, twt_countdown = operations.append_available(
        results=[],
        args=args,
        twt_countdown=3,
        start_time='0'
    )
    assert (boolean, twt_countdown) == (True, 1)
