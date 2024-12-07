import pytest
from app import create_app, db
from app.models import Player, PlayerRank
from flask import url_for
from app.scripts.setup_test_db import populate_test_db


@pytest.fixture
def client():
    """
    Pytest fixture for creating a test client.

    This fixture:
    - Initializes the Flask app with the 'testing' configuration.
    - Configures the database to drop and recreate all tables before each test.
    - Populates the test database with sample data using `populate_test_db`.

    Yields:
        Flask test client for simulating HTTP requests.
    """
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'

    with app.app_context():
        db.create_all()
        db.drop_all()

        populate_test_db()
        yield app.test_client()


def test_team_table(client):
    """
    Test the homepage populates with teams.

    Steps:
    1. Access the homepage using the test client.
    2. Assert that a known test team (e.g., "Test Team") is present in the response data.

    Expected Outcome:
    - The homepage contains the test team's name, indicating teams are correctly loaded.
    """
    with client.application.app_context():
        response = client.get(url_for('main.index'))

    assert b'Test Team' in response.data


def test_team_table_empty(client):
    """
    Test the homepage behavior when no teams exist.

    Steps:
    1. Drop all database tables to simulate an empty database.
    2. Access the homepage using the test client.
    3. Assert that a "Missing" message or link is displayed.
    4. Assert that the response status code is 404.

    Expected Outcome:
    - The homepage indicates that no teams are available.
    """
    with client.application.app_context():
        db.drop_all()
        db.create_all()  # Recreate tables to avoid missing table errors
        response = client.get(url_for('main.index'))

    assert response.status_code == 404
    assert b">Missing<" in response.data


def test_player_not_found(client):
    """
    Test the player profile page behavior when a player does not exist.

    Steps:
    1. Attempt to access the profile page for a non-existent player (e.g., `player_id=999999`).
    2. Assert that the response contains the "Player not found" error message.
    3. Assert that the response status code is 404.

    Expected Outcome:
    - The player profile page returns a "Player not found" message and a 404 status code.
    """
    with client.application.app_context():
        response = client.get(url_for('main.player_profile', player_id=999999))

    assert b'Player not found' in response.data
    assert response.status_code == 404


def test_player_profile_found(client):
    """
    Test the player profile page behavior when a player exists.

    Steps:
    1. Access the profile page for a known test player (`player_id=1`).
    2. Assert that the response contains the player's name and associated stats.
    3. Assert that the response status code is 200.

    Expected Outcome:
    - The player profile page displays the test player's details, including name, team, and stats.
    """
    with client.application.app_context():
        response = client.get(url_for('main.player_profile', player_id=1))

    assert b'Test Player' in response.data
    assert b'Test Team' in response.data
    assert b'99<sup>th</sup> Percentile' in response.data
    assert response.status_code == 200


def test_produce_tasks(client, mocker):
    """
    Test the /produce_tasks endpoint.

    Steps:
    1. Mock the `publish_task` function to simulate successful task publishing.
    2. Trigger the `produce_tasks` endpoint via a POST request.
    3. Assert that the response status code is 200.
    4. Assert that the response contains a success message.

    Expected Outcome:
    - The /produce_tasks endpoint successfully triggers task publishing and returns a success message.
    """
    mock_publish = mocker.patch('app.scripts.producer.publish_task')
    mock_publish.side_effect = None  # Simulate successful task publishing

    response = client.post(url_for('main.produce_tasks'))
    assert response.status_code == 200
    assert b"Tasks successfully added to queue." in response.data