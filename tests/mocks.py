from seventweets.client import Client


class MockClientResponse(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json(self):
        return self.content


data = [
    {'id': 2, 'name': 'drugi', 'type': 'original',
     'creation_time': '2010-01-01', 'tweet': 'joyful day'},
    {'id': 3, 'name': 'drugi', 'type': 'original',
     'creation_time': '2010-01-02', 'tweet': 'test tweet 1'},
    {'id': 4, 'name': 'drugi', 'type': 'original',
     'creation_time': '2010-01-03', 'tweet': 'test tweet 2'},
    {'id': 5, 'name': 'drugi', 'type': 'retweet',
     'creation_time': '2010-01-04', 'tweet': 'test tweet 1'},
    {'id': 6, 'name': 'drugi', 'type': 'original',
     'creation_time': '2010-01-05', 'tweet': 'test tweet 3'},
    {'id': 7, 'name': 'drugi', 'type': 'retweet',
     'creation_time': '2010-01-06', 'tweet': 'test tweet 3'}
]


def mock_search_me(args):
    data_copy = data.copy()
    if args['content']:
        for elm in data_copy.copy():
            if elm['tweet'].find(args['content']) < 0:
                data_copy.remove(elm)
    if args['from_time']:
        for elm in data_copy.copy():
            if elm['creation_time'] < args['from_time']:
                data_copy.remove(elm)
    if args['to_time']:
        for elm in data_copy.copy():
            if elm['creation_time'] > args['to_time']:
                data_copy.remove(elm)
    if args['per_page']:
        if args['last_creation_time']:
            for elm in data_copy.copy():
                if elm['creation_time'] <= args['last_creation_time']:
                    data_copy.remove(elm)
            result = sorted(
                data_copy,
                key=lambda elm: elm['creation_time']
            )[:int(args['per_page']) if args['per_page'] else None]

        else:
            result = sorted(
                data_copy,
                key=lambda elm: elm['creation_time']
            )[:int(args['per_page']) if args['per_page'] else None]

    else:
        result = data_copy

    if result:
        return MockClientResponse(status_code=200, content=result)
    else:
        return MockClientResponse(status_code=404, content=None)


def mock_get_tweet(id):
    return {}


def mock_register(data):
    return MockClientResponse(status_code=200, content={'status': 'ok'})


def mock_unregister(data):
    return MockClientResponse(status_code=200, content={'status': 'ok'})


Client.search_me = mock_search_me
Client.get_tweet = mock_get_tweet
Client.register = mock_register
Client.unregister = mock_unregister
