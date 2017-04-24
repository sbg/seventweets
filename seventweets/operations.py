import logging

from seventweets.config import g
from seventweets.exceptions import NotFound

from seventweets import db

logger = logging.getLogger(__name__)


def connect_to_all_servers():
    """
    Sends register requests to all servers in network
    :return:
    """
    for name in g.registry.servers.keys():
        if name != g.my_name:
            client = g.get_client(server_name=name)
            client.register(
                    {
                        'name': g.my_name,
                        'port': g.port
                    }
                )


def connect_to_server():
    """
    Sends register request to one server who's address was supplied
    in the command line
    :return: Server's response - json with all servers addresses and names
    """
    client = g.get_client(server_address=g.connect_to)
    return client.register(
        {
            'name': g.my_name,
            'port': g.port
        }
    )


def unregister_from_servers():
    """
    Sends unregister requests to all servers
    :return:
    """
    for name in g.registry.servers.keys():
        if name != g.my_name:
            client = g.get_client(server_name=name)
            client.unregister(g.my_name)


def get_tweets():
    """
    Gets all tweets from local database
    :return: Sorted list of tweets
    """
    results = []
    for row in db.get_all_tweets():
        result = get_tweet_content(row)
        if result:
            results.append(result)
    if not results:
        raise NotFound('No tweets from this server')

    return sorted(results, key=lambda elm: elm['creation_time'])


def get_tweet(id):
    """
    Gets tweet from local database with supplied id
    :param id: id of the tweet
    :return: one tweet as dict
    """
    result = None
    for row in db.get_tweet_by_id(id):
        result = get_tweet_content(row)
    if not result:
        raise NotFound('id not found')
    return result


def delete_tweet(id):
    """
    Deletes tweet with supplied id if id exists
    :param id: id of the tweet
    :return:
    """
    result = db.delete_tweet(id)
    if not result:
        raise NotFound('id not found, nothing to delete')


def modify_tweet(tweet, id):
    """
    Modifies content of the tweet with supplied id
    :param tweet: new content
    :param id: id of the tweet that has to be modified
    :return:
    """
    result = db.modify_tweet(tweet=tweet, id=id)
    if not result:
        raise NotFound('id not found, nothing to modify')


def get_tweet_content(row):
    """
    Checks if tweet is of type original or re-tweet. If tweet is re-tweet
    try to acquire content from original server where tweet is perserved.
    :param row: tweet row from the table tweets
    :return: tweet as dict
    """
    result = {
        'id': row[0],
        'name': row[1],
        'tweet': row[2],
        'creation_time': row[3],
        'type': row[4],
        'reference': row[5]
    }
    if row[5]:
        try:
            reference = row[5].split('#')
            if reference[0] == g.my_name:
                db_result_row = db.get_tweet_by_id(reference[1])[0]
                result['tweet'] = db_result_row[2]
                possible_reference = db_result_row[5]
                # re tweet on re tweet situation
                if not result['tweet']:
                    row[5] = possible_reference
                    result['tweet'] = get_tweet_content(row)['tweet']
            else:
                response = g.get_client(
                    server_name=reference[0]
                ).get_tweet(reference[1])
                result['tweet'] = response.json()['tweet']
        except Exception as e:
            logger.debug('Error getting tweet through reference', exc_info=e)
            result = None
    return result


def examine_tweets_from_all_servers(args):
    """
    Sends search_me requests to all active servers and aggregates results
    :param args: Object containing search params
    :return: list of found tweets
    """
    results = []
    for name in g.registry.servers.keys():
        if name == g.my_name:
            try:
                results.extend(examine_tweets_from_this_server(args))
            except Exception as e:
                logger.debug('No tweets from this server', exc_info=e)
        else:
            client = g.get_client(server_name=name)
            r = client.search_me(args.to_dict())
            if r.status_code == 200:
                results.extend(r.json())
            else:
                logger.error(
                    'Server {} reported status: {}'.format(name, r.status_code)
                )
    if not results:
        raise NotFound('No search results')

    return results


def find_tweets(args):
    """
    Manages search for tweets(checks if username is search param and then
    guides searching algorithm).
    :param args: Object containing search params
    :return: Final search results sorted  and last_time if paging is required
    else 0
    """
    results = []
    if args.name is None:
        results.extend(examine_tweets_from_all_servers(args))
    elif args.name == g.my_name:
        results.extend(examine_tweets_from_this_server(args))
    elif g.registry.servers.get(args.name):
        r = g.get_client(server_name=args.name).search_me(args.to_dict())
        if r.status_code == 200:
            results.extend(r.json())
        else:
            logger.error('Server reported status: {}'.format(r.status_code))
    else:
        raise NotFound('Server with that name does not exists')
    if not results:
        raise NotFound('No search results')

    return sort_and_cut_results(results, args)


def sort_and_cut_results(results, args):
    """
    Sorts results(per creation time of the tweet) of the search and
    slice's list if paging is required
    :param results: Search results
    :param args: Object containing search params
    :return: Sorted results and creation time of the last tweet in the list or
    0 if paging is off
    """

    final_results = sorted(
        results,
        key=lambda elm: elm['creation_time']
    )[:int(args.per_page) if args.per_page else None]

    last_time = '0'
    if args.per_page and (len(results) >= int(args.per_page)):
        last_time = final_results[-1]['creation_time']
    logger.debug('last_time : '+last_time + ' final_results: '
                 + str(final_results))
    return final_results, last_time


def examine_tweets_from_this_server(args):
    """
    Searches through all types of tweets on this server
    :param args: Object containing search params
    :return: list of found tweets
    """
    results = []
    results.extend(search_original_tweets(args))
    results.extend(search_re_tweets(args))

    if not results:
        raise NotFound('No search results')

    return results


def search_original_tweets(args):
    """
    Searches only through local original tweets and gets their content
    :param args: Object containing search params
    :return: list of found tweets
    """
    results = []
    for row in db.search_tweets(args=args, retweet=False):
        result = get_tweet_content(row)
        results.append(result)
    return results


def search_re_tweets(args):
    """
    Searches only through local re-tweets and tries to get their content
    :param args: Object containing search params
    :return: list of found tweets
    """

    results = []
    if args.per_page is None:
        for row in db.search_tweets(args=args, retweet=True):
            result = get_tweet_content(row)
            if args.content and result and result.get('tweet'):
                if result['tweet'].find(args.content) >= 0:
                    results.append(result)
            elif result and result.get('tweet'):
                results.append(result)
    else:
        start_time = '0'
        twt_countdown = int(args.per_page)
        if args.last_creation_time:
            start_time = args.last_creation_time

        re_tweet_unavailable, start_time, twt_countdown = append_available(
            results=results,
            args=args,
            twt_countdown=twt_countdown,
            start_time=start_time
        )
        while twt_countdown and re_tweet_unavailable:
            re_tweet_unavailable, start_time, twt_countdown = append_available(
                results=results,
                args=args,
                twt_countdown=twt_countdown,
                start_time=start_time
            )
    return results


def append_available(results, args, twt_countdown, start_time):
    """
    Checks if re-tweet content is available and appends to results. If re-tweet
    content is unavailable then return from function. Also if content matching
    is required check for match in the current tweet and if match is not
    found return from function.
    :param results: Current results
    :param args: Object with search params
    :param twt_countdown: How many more tweets needs to be added to results
    :param start_time: creation time of the last element on the last page
    :return: values for re_tweet_unavailable, start_time and stack
    """

    for row in db.get_retweets_refined(args=args, start_time=start_time):
        if twt_countdown == 0:
            return False, 0, 0
        result = get_tweet_content(row)
        if args.content and result and result.get('tweet'):
            if result['tweet'].find(args.content) >= 0:
                results.append(result)
                twt_countdown -= 1
            else:
                return True, row[3], twt_countdown
        elif result and result.get('tweet'):
            results.append(result)
            twt_countdown -= 1
        else:
            return True, row[3], twt_countdown
    return False, 0, 0
