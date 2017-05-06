"""
SevenTweets HTTP client implementation.
"""

import copy
import requests
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RetryError, ConnectionError, ConnectTimeout
from seventweets import exceptions


class Client:
    """
    Client for seventweets. Since all seventweets servers share same API,
    this client is used to communicate with other nodes in the mash.
    """
    _exceptions = {
        400: exceptions.BadRequest,
        401: exceptions.Unauthorized,
        403: exceptions.Forbidden,
        404: exceptions.NotFound,
        409: exceptions.Conflict,
        500: exceptions.ServerError,
        502: exceptions.BadGateway,
        503: exceptions.ServiceUnavailable,
    }

    def __init__(self, address, default_headers=None, cleanup_callback=None):
        self.address = address
        self._session = None
        self.default_headers = default_headers or {
            'Content-Type': 'application/json'
        }
        self.cleanup_callback = cleanup_callback

    @property
    def session(self):
        """
        Returns session for maintaining open connections to servers.
        """
        if not hasattr(self, '_session') or not self._session:
            self._session = requests.session()
            # sane defaults for retry policy
            retries = Retry(total=3, backoff_factor=1,
                            status_forcelist=[502, 503, 504])
            self._session.mount('http://', HTTPAdapter(max_retries=retries))
            self._session.mount('https://', HTTPAdapter(max_retries=retries))
        return self._session

    def _request(self, method, path, params=None, data=None, headers=None):
        """
        Sends requests, checks response for errors and returns
        :param method: HTTP verb to use for request.
        :type method: str
        :param path: Path on remote server to send request to.
        :type path: str
        :param params: Query parameters to include in request.
        :type params: dict
        :param data: Body data to send with request.
        :type data: object
        :param headers: Additional headers to include in request.
        :type headers: dict
        :return: Response body returned from server.
        :raises: HttpException subclass, if response status code is not valid.
        """
        all_headers = copy.copy(self.default_headers)
        all_headers.update(headers or {})
        url = '{}{}'.format(self.address, path)
        try:
            resp = self.session.request(
                method, url, params=params, json=data, headers=all_headers
            )

            self._raise(resp)
            # check if there's a body
            if resp.status_code != 204:
                return resp.json()

        except (RetryError, ConnectionError, ConnectTimeout):
            self.cleanup_callback()
            raise exceptions.BadGateway(
                'The node you provided is unreachable.'
            )

    def _raise(self, response):
        """
        Based on provided response, raises appropriate HttpException.

        This method does not return meaningful result, it is useful only
        for its side effect.

        :param response: Response received from server.
        """
        exc = self._exceptions.get(response.status_code, None)
        if exc is not None:
            raise exc(response)

    def register(self, data, force_update=False):
        return self._request('POST', '/registry/', data=data,
                             params={'force': force_update})

    def unregister(self, name):
        self._request('DELETE', '/registry/{}'.format(name))

    def update_tweet(self, tweet, tweet_id):
        return self._request(
            'PUT', '/tweets/{}'.format(id), data={'tweet': tweet}
        )

    def delete_tweet(self, tweet_id):
        return self._request('DELETE', '/tweets/{}'.format(tweet_id))

    def create_tweet(self, tweet):
        self._request('POST', '/tweets', data={'tweet': tweet})

    def create_retweet(self, name, tweet_id):
        self._request('POST', '/retweet',
                      data={'name': name, 'id': tweet_id})

    def get_tweet(self, tweet_id):
        return self._request('GET', '/tweets/{}'.format(tweet_id))

    def get_tweets(self):
        return self._request('GET', '/tweets')

    def search(self, content: str=None,
               from_created: datetime=None,
               to_created: datetime=None,
               from_modified: datetime=None,
               to_modified: datetime=None,
               retweet: bool=None,
               all: bool=False):
        return self._request('GET', '/tweets/search', params={
            'content': content if content else '',
            'created_from': from_created.timestamp() if from_created else '',
            'created_to': to_created.timestamp() if to_created else '',
            'modified_from': (from_modified.timestamp()
                              if from_modified else ''),
            'modified_to': to_modified.time() if to_modified else '',
            'retweet': 'true' if retweet else 'false',
            'all': 'true' if all else 'false',
        })

    def search_me(self, params):
        return self._request('GET', '/search_me', params=params)
