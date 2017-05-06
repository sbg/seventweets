from seventweets.utils import generate_api_token


def test_generate_api_token():
    # since this should be random, just test if two consequent calls
    # did not return same result
    assert generate_api_token() != generate_api_token()

    assert type(generate_api_token()) is str
