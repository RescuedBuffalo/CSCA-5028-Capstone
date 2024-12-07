"""
Integration tests for the application's routes.

This file:
- Tests the interaction between the application's routes, database, and test client.
- Validates that teams, rosters, and player profiles are correctly populated and accessible via HTTP requests.

Dependencies:
- `pytest` for managing test cases and fixtures.
- Flask app and SQLAlchemy for database and application context.
- `dotenv` for loading environment variables.
- `flask_migrate` for managing database migrations.
- `app.models` for database models.

Fixtures:
- `client`: Sets up the Flask app and database for testing and provides a test client.

Test Cases:
- `test_player_lookup`: Ensures teams, rosters, and player profiles can be looked up and display the correct data.

Preconditions:
- The database must be initialized with test data using `populate_test_db`.
- Environment variables must be loaded to configure the app correctly.
"""

import pytest
from app import create_app, db
from dotenv import load_dotenv
from app.scripts.setup_test_db import populate_test_db
from flask_migrate import Migrate
from app.models import Team

@pytest.fixture
def client():
    """
    Pytest fixture to provide a test client for the Flask app.

    This fixture:
    - Loads environment variables using `dotenv`.
    - Creates the Flask app in testing mode.
    - Drops and recreates all database tables before each test.
    - Populates the database with test data.

    Yields:
        Flask test client for HTTP request simulation.
    """
    load_dotenv()  # Load environment variables

    # Create the app instance for testing
    app = create_app('testing')

    with app.app_context():
        # Set up the database for testing
        db.drop_all()
        db.create_all()
        populate_test_db()

    yield app.test_client()  # Provide the test client


def test_player_lookup(client):
    """
    Test the lookup flow for teams, rosters, and player profiles.

    Steps:
    1. Access the homepage and verify it displays the test team.
    2. Extract the team ID from the homepage response.
    3. Access the team's roster page using the extracted team ID and verify it displays the test player.
    4. Extract the player ID from the roster page response.
    5. Access the player's profile page using the extracted player ID and verify it displays the player's information.

    Expected Outcome:
    - The homepage correctly displays the test team.
    - The team's roster page correctly displays the test player's information.
    - The player's profile page correctly displays the player's details.
    """
    # Test to ensure the homepage is populating with teams
    response = client.get('/')
    assert b'Test Team' in response.data, "Homepage does not display the test team."

    # Extract the team_id from the response
    team_id = response.data.split(b'href="/team/')[1].split(b'"')[0].decode()
    assert team_id == '9999', f"Expected team ID '9999', got {team_id}."

    # Test to ensure we can get the team's roster
    response = client.get(f'/team/{team_id}')
    assert b'Test Player' in response.data, "Team roster does not display the test player."

    # Extract the player_id from the response
    player_id = response.data.split(b'href="/player/')[1].split(b'"')[0].decode()
    assert player_id == '1', f"Expected player ID '1', got {player_id}."

    # Test to ensure we can get the player's profile
    response = client.get(f'/player/{player_id}')
    assert b'Test Player' in response.data, "Player profile does not display the player's details."

def test_empty_database(client):
    """
    Test the application's behavior when the database is empty.

    Steps:
    1. Clear the database.
    2. Access the homepage and verify it displays an appropriate error message.
    3. Access a team page and verify it displays an appropriate error message.
    4. Access a player page and verify it displays an appropriate error message.

    Expected Outcome:
    - The application responds gracefully with proper error messages for all routes.
    """
    with client.application.app_context():
        db.drop_all()
        db.create_all()  

    response = client.get('/')
    assert response.status_code == 404
    assert b">Missing<" in response.data, "Expected a message for an empty homepage."

    response = client.get('/team/00000000')
    assert response.status_code == 404
    assert b"No players found for this team." in response.data, "Expected an error message for a missing team."

    response = client.get('/player/000000')
    assert response.status_code == 404
    assert b"Player not found." in response.data, "Expected an error message for a missing player."

def test_non_existent_team_or_player(client):
    """
    Test accessing non-existent teams or players.

    Steps:
    1. Access a team page for a non-existent team ID.
    2. Access a player page for a non-existent player ID.

    Expected Outcome:
    - Both routes respond with 404 and display an appropriate error message.
    """
    response = client.get('/team/0000000000')  # Non-existent team ID
    assert response.status_code == 404
    assert b"No players found for this team." in response.data, "Expected an error message for a non-existent team."

    response = client.get('/player/0000000000')  # Non-existent player ID
    assert response.status_code == 404
    assert b"Player not found." in response.data, "Expected an error message for a non-existent player."

def test_team_with_no_players(client):
    """
    Test the behavior of a team page with no associated players.

    Steps:
    1. Add a team to the database without any players.
    2. Access the team's page and verify it displays an appropriate error message.

    Expected Outcome:
    - The team page displays a message indicating the roster is empty.
    """
    with client.application.app_context():
        db.create_all()
        team = Team(team_id=1, full_name="Empty Team", tricode="ETM", raw_tricode="ETM_RAW", league_id=1)
        db.session.add(team)
        db.session.commit()

    response = client.get('/team/1')
    assert response.status_code == 404
    assert b"No players found for this team." in response.data, "Expected an error message for a team with no players."