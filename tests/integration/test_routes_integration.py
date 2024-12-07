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
        db.drop_all()
        db.create_all()
        populate_test_db()

    yield app.test_client()

def test_player_lookup(client):
    # Test to ensure the the homepage is populating with teams
    response = client.get('/')
    assert b'Test Team' in response.data

    # Get the team_id from the response
    team_id = response.data.split(b'href="/team/')[1].split(b'"')[0].decode()
    assert team_id == '9999'

    # Test to ensure we can get the team's roster
    response = client.get(f'/team/9999')
    assert b'Test Player' in response.data

    # Get the player_id from the response
    player_id = response.data.split(b'href="/player/')[1].split(b'"')[0].decode()
    assert player_id == '1'

    # Test to ensure we can get the player's profile
    response = client.get(f'/player/{player_id}')
    assert b'Test Player' in response.data

    