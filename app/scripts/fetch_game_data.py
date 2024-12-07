"""
Script for fetching and storing game data for NHL players.

This script:
- Fetches game logs for all players from the NHL stats API.
- Saves the game data into the `GameLog` database table, avoiding duplicate entries.
- Supports data fetching for the regular season or playoffs.

Dependencies:
- `requests` for making HTTP requests to the NHL stats API.
- Flask app and SQLAlchemy models for database interactions.

Usage:
Run this script to fetch and save game data for all players in the database.

Environment Variables:
- `CONFIG_NAME`: The Flask configuration name (e.g., development, production).
- `SQLALCHEMY_DATABASE_URI`: The database connection URI.

Preconditions:
- The database must be populated with players.
- The API endpoint must be accessible.

Example:
    python fetch_game_data.py
"""

import requests
from app import db, create_app
from app.models import Player, GameLog
import os
from dotenv import load_dotenv

def fetch_game_data():
    """
    Fetch game logs for all players and save them to the database.

    Steps:
    1. Retrieve all players from the `Player` database table.
    2. For each player, fetch their game logs for the current season and sub-season.
    3. Check if the game log already exists in the `GameLog` table to avoid duplicates.
    4. Save new game logs to the database.

    API Endpoint:
        - Base URL: `https://api-web.nhle.com/v1/player/{player_id}/game-log/{season}/{sub_season}`
        - Parameters:
            - `player_id`: Unique ID of the player.
            - `season`: NHL season (e.g., "20242025").
            - `sub_season`: "2" for regular season, "3" for playoffs.

    Raises:
        - Exception if database commits fail.
    """
    # Retrieve all players from the database
    players = Player.query.all()

    # Define the current season and sub-season (hardcoded for now)
    season = "20242025"  # Dynamically set this if needed
    sub_season = "2"  # "2" = regular season, "3" = playoffs

    for player in players:
        # Construct the game log API URL
        game_log_url = f'https://api-web.nhle.com/v1/player/{player.player_id}/game-log/{season}/{sub_season}'

        # Fetch game logs from the API
        response = requests.get(game_log_url)

        if response.status_code == 200:
            # Parse game logs from the API response
            game_logs = response.json().get('gameLog', [])

            for game in game_logs:
                # Check if the game log already exists in the database
                existing_log = GameLog.query.filter_by(player_id=player.player_id, game_id=game['gameId']).first()

                if not existing_log:
                    # Create a new game log entry
                    new_game_log = GameLog(
                        player_id=player.player_id,
                        game_id=game['gameId'],
                        game_date=game['gameDate'],
                        opponent=game.get('opponentCommonName', {}).get('default', ''),
                        home_road_flag=game['homeRoadFlag'],
                        goals=game['goals'],
                        assists=game['assists'],
                        points=game['points'],
                        shots=game['shots'],
                        plus_minus=game['plusMinus'],
                        power_play_goals=game['powerPlayGoals'],
                        pim=game['pim'],
                        toi=game['toi']
                    )
                    # Add the new game log to the session
                    db.session.add(new_game_log)
        else:
            # Log an error if the API request fails
            print(f"Failed to fetch game logs for player {player.player_id}. Status Code: {response.status_code}")

    # Commit the session to save changes to the database
    try:
        db.session.commit()
        print('Data saved successfully to {}'.format(os.getenv('SQLALCHEMY_DATABASE_URI')))
        db.session.close()
    except Exception as e:
        # Rollback the session if there is an error
        db.session.rollback()
        print(f"Error saving data: {e}")
        db.session.close()

# Load environment variables from a .env file
load_dotenv('.env')

# Create the Flask app instance based on the environment configuration
config_name = os.getenv('CONFIG_NAME')
app = create_app(config_name=config_name)

if __name__ == '__main__':
    """
    Entry point for the script.

    Ensures the Flask app context is available for database interactions.
    """
    with app.app_context():
        fetch_game_data()