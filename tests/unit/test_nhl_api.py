import pytest
from app.utils.nhl_api import get_nhl_player_stats
import requests
from unittest.mock import patch
from dotenv import load_dotenv
from app import create_app
from app.scripts.setup_test_db import populate_test_db
from app.models import Player

@pytest.fixture
def app():
    app = create_app('testing')
    app.testing = True
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

@patch('app.models.Player.query')
def test_get_nhl_player_stats_db_hit(mock_query, app):
    # Simulate a database hit
    mock_query.filter_by.return_value.first.return_value = Player(
        player_id=1, 
        first_name='Player', 
        last_name='One', 
        team_name='Team', 
        position='Forward', 
        jersey_number=1, 
        headshot='', 
        birth_city='City', 
        birth_province='Province', 
        birth_country='Country', 
        height_in_inches=70, 
        weight_in_pounds=180, 
        points_per_game=0.8, 
        goals_per_game=0.5, 
        avg_toi='20:10', 
        shooting_pct=12.5, 
        games_played=50, 
        goals=25, 
        assists=20,
        points=45, 
        shots=150, 
        power_play_goals=5)

    # Call the function with a sample player ID
    result = get_nhl_player_stats(1)

    # Test that it returns the expected result
    assert result['first_name'] == 'Player'
    assert result['last_name'] == 'One'
    assert result['team_name'] == 'Team'

@patch('app.models.Player.query')
def test_get_nhl_player_stats_api_error(mock_get, app):
    # Simulate a failed API call (e.g., 404 Not Found)
    mock_get.filter_by.return_value.first.return_value = None

    # Call the function with a sample player ID
    result = get_nhl_player_stats(99)

    # Test that it returns None or raises the expected error
    assert result is '404'