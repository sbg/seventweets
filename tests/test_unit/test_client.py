from seventweets.client import Client


def test_create_url_method():

    client = Client('127.0.0.1:5000')
    path = '/tweets'
    assert client._create_url(path) == 'http://127.0.0.1:5000/tweets'


