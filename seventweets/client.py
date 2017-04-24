import requests


class Client:
    """
    Class for handling communication with other servers.
    One instance of the Client is responsible for one other server.
    """

    def __init__(self, address):
        """
        Initialize Client with server address
        :param address: Server with whom Client instance communicates
        """
        self.address = address

    def _create_url(self, path):
        """
        Creates url string
        :param path: endpoint
        :return:  string url
        """
        return 'http://{}{}'.format(self.address, path)

    @staticmethod
    def _request(method, url, params=None, data=None,
                 headers={'content-type': 'application/json'}):
        """
        Method for handling all types of requests
        :param method: request method type
        :param url: sending request to this url
        :param params: params of the request that goes to query string
        :param data: data that goes to the body of the request
        :param headers: header fields of the request
        :return: Response of the request
        """

        if method == 'GET':
            return requests.get(url, params=params, headers=headers)
        elif method == 'DELETE':
            return requests.delete(url, headers=headers)
        elif method == 'POST':
            return requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            return requests.put(url, json=data, headers=headers)

    def register(self, data):
        """
        Sends register request to another server
        :param data: body of the request
        :return: Response of the request
        """
        return self._request(method='POST', url=self._create_url('/register'),
                             data=data)

    def unregister(self, name):
        """
        Sends unregister request to another server
        :param name: Name of server that sends request
        :return:
        """
        return self._request(method='DELETE',
                             url=self._create_url('/unregister/' + name))

    def update_tweet(self, tweet, id):
        return self._request(method='PUT', url=self._create_url(
            '/tweets/' + str(id)), data={'tweet': tweet})

    def delete_tweet(self, id):
        return self._request(method='DELETE',
                             url=self._create_url('/tweets/' + str(id)))

    def create_tweet(self, tweet):
        return self._request(method='POST', url=self._create_url('/tweets'),
                             data={'tweet': tweet})

    def create_re_tweet(self, name, id):
        return self._request(method='POST', url=self._create_url('/retweet'),
                             data={'name': name, 'id': id})

    def get_tweet(self, id):
        return self._request(method='GET',
                             url=self._create_url('/tweets/' + str(id)))

    def get_tweets(self):
        return self._request(method='GET', url=self._create_url('/tweets'))

    def search(self, params):
        return self._request(method='GET', url=self._create_url('/search'),
                             params=params)

    def search_me(self, params):
        return self._request(method='GET', url=self._create_url('/search_me'),
                             params=params)
