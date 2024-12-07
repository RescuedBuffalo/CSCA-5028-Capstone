import pytest
from app import create_app, db
from app.models import Player
from flask import url_for

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

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
    player = Player(player_id=123, first_name='John', last_name='Doe', team_name='Sharks',
                    position='Forward', jersey_number=12, headshot='', birth_city='City', birth_province='Province',
                    birth_country='Country', height_in_inches=70, weight_in_pounds=180, points_per_game=0.8,
                    goals_per_game=0.5, avg_toi='20:10', shooting_pct=12.5, games_played=50, goals=25, assists=20,
                    points=45, rank=40, shots=150, power_play_goals=5)
    db.session.add(player)
    db.session.commit()

    # Simulate a request context to enable url_for to work
    with client.application.app_context():
        # Simulate visiting the player profile page for the newly created player
        response = client.get(url_for('main.player_profile', player_id=123))

    # Assert that the response contains the player's name and other stats
    assert b'John Doe' in response.data
    assert b'Sharks' in response.data
    assert b'40<sup>th</sup> Percentile' in response.data
    assert response.status_code == 200


def test_produce_tasks(client):
    response = client.get(url_for('main.produce_tasks'))
    assert response.status_code == 200
    assert b'Tasks successfully added to queue.' in response.data