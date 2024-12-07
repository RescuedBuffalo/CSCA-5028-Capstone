import pytest
from app import create_app, db
from app.models import Player, PlayerRank
from flask import url_for
from app.scripts.setup_test_db import populate_test_db

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'

    with app.app_context():
        db.create_all()
        db.drop_all()

        populate_test_db()
        yield app.test_client()


def test_team_table(client):
    # Test to ensure the the homepage is populating with teams
    with client.application.app_context():
        response = client.get(url_for('main.index'))

    # write response.data to a file
    with open('response.data', 'wb') as f:
        f.write(response.data)

    assert b'Test Team' in response.data

def test_team_table_empty(client):
    # Test to ensure the the homepage is populating with teams
    with client.application.app_context():
        db.drop_all()
        response = client.get(url_for('main.index'))

    assert response.status_code == 404
    assert b'<a href="#">Missing</a>' in response.data

def test_player_not_found(client):
    # Simulate a request context to enable url_for to work
    with client.application.app_context():
        # Simulate visiting a player profile page for a player that doesn't exist
        response = client.get(url_for('main.player_profile', player_id=999999))

    # Assert that the response contains the 'Player not found' error message
    assert b'Player not found' in response.data
    
    # Assert that the response returns the 404 status code
    assert response.status_code == 404


def test_player_profile_found(client):
    # Create a dummy player in the test database

    # Simulate a request context to enable url_for to work
    with client.application.app_context():
        # Simulate visiting the player profile page for the newly created player
        response = client.get(url_for('main.player_profile', player_id=1))

    # Assert that the response contains the player's name and other stats
    assert b'Test Player' in response.data
    assert b'Test Team' in response.data
    assert b'0.5<sup>th</sup> Percentile' in response.data
    assert response.status_code == 200


def test_produce_tasks(client):
    response = client.post(url_for('main.produce_tasks'))
    assert response.status_code == 200
    assert b'Tasks successfully added to queue.' in response.data