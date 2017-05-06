import os
import importlib
import pytest
from unittest.mock import patch


def test_config_default_values():
    from seventweets import config
    assert config.ST_DB_HOST == 'localhost'
    assert config.ST_DB_PORT == 5432
    assert config.ST_DB_USER == 'workshop'
    assert config.ST_DB_PASS is None
    assert config.ST_DB_NAME == 'seventweets'
    assert config.ST_OWN_NAME is None
    assert config.ST_OWN_ADDRESS is None
    assert config.ST_API_TOKEN is None


@pytest.mark.parametrize(
    argnames=('env_var', 'env_value', 'config_name'),
    argvalues=(
        ('ST_DB_HOST', 'some_host', 'ST_DB_HOST'),
        ('ST_DB_PORT', '1111', 'ST_DB_PORT'),
        ('ST_DB_USER', 'some user', 'ST_DB_USER'),
        ('ST_DB_PASS', 'random password', 'ST_DB_PASS'),
        ('ST_DB_NAME', 'db name', 'ST_DB_NAME'),
        ('ST_OWN_NAME', 'server name', 'ST_OWN_NAME'),
        ('ST_OWN_ADDRESS', 'http://own_address', 'ST_OWN_ADDRESS'),
        ('ST_API_TOKEN', 'randomToken', 'ST_API_TOKEN'),
    ),
    ids=['host', 'port', 'user', 'pass', 'name', 'own_name',
         'address', 'token']
)
def test_config_overrides(env_var, env_value, config_name):
    with patch.dict(os.environ, {env_var: env_value}):
        from seventweets import config
        # we have to reload module since it is once loaded and cached
        importlib.reload(config)
        # del sys.modules['seventweets.config']

        assert getattr(config, config_name) == env_value
