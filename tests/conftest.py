import pytest
from unittest.mock import patch


@pytest.fixture
def app():
    from seventweets.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app
