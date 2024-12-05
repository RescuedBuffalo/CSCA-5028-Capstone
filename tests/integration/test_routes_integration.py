import pytest
from app import create_app, db
from dotenv import load_dotenv
from app.scripts.setup_test_db import populate_test_db
from flask_migrate import Migrate

@pytest.fixture
def client():
    load_dotenv()

    app = create_app('testing')

    with app.app_context():
        populate_test_db()

    yield app.test_client()

def test_player_lookup(client):
    # simulate a user making a request on / and then the corresponding results on /player/{id}
    # create a payload that is a form with player_id = 1
    payload = {'player_id': 1}
    response = client.post('/', data=payload, follow_redirects=True)

    # assert that we were redirected to /player/8478402
    assert response.status_code == 200
    assert b"Player Stats" in response.data

    # assert that the player's name is displayed
    assert b"Test Player" in response.data

    