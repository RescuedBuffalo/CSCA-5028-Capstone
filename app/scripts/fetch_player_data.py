"""
Script for fetching and updating player data from the NHL API.

This script:
- Fetches player stats from the NHL stats API.
- Analyzes the performance of players.
- Updates or inserts player information into the database.

Dependencies:
- `requests` for making HTTP requests to the NHL stats API.
- `dotenv` for loading environment variables.
- Flask app and SQLAlchemy for database interactions.

Usage:
Run this script to fetch and save player data for all players listed in the roster.

Environment Variables:
- `CONFIG_NAME`: The Flask configuration name (e.g., development, production).
- `SQLALCHEMY_DATABASE_URI`: The database connection URI.

Example:
    python fetch_player_data.py
"""

from app import db, create_app
from app.models import Player, Roster
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance
import os
from dotenv import load_dotenv


def fetch_player_data(config='production'):
    """
    Fetch and update player data from the NHL API.

    Steps:
    1. Retrieve player IDs from the `Roster` database table.
    2. For each player:
       a. Fetch player stats from the NHL stats API.
       b. Analyze the player's performance using custom analysis logic.
       c. Update the `Player` database table with new stats or insert a new record.
    3. Commit all changes to the database.

    Args:
        config (str): The application configuration name (default: 'production').

    Raises:
        Exception: Rolls back the transaction if database commit fails.
    """
    # Retrieve all unique player IDs from the roster
    player_ids = db.session.query(Roster.player_id).distinct().all()

    for player_id in player_ids:
        player_id = player_id[0]  # Extract the player ID from the tuple

        # Fetch player data from the NHL API
        player_data = get_nhl_player_stats(player_id)

        if player_data:
            # Analyze the player's performance
            processed_data = analyze_player_performance(player_data)

            # Check if the player already exists in the database
            existing_player = Player.query.filter_by(player_id=player_id).first()

            if existing_player and processed_data.get("career_stats", None) is not None:
                # Update the existing player's information
                existing_player.first_name = processed_data["player_info"]["first_name"]
                existing_player.last_name = processed_data["player_info"]["last_name"]
                existing_player.team_name = processed_data["player_info"]["team_name"]
                existing_player.position = processed_data["player_info"]["position"]
                existing_player.jersey_number = processed_data["player_info"]["jersey_number"]
                existing_player.headshot = processed_data["player_info"]["headshot"]
                existing_player.birth_city = processed_data["player_info"]["birth_city"]
                existing_player.birth_province = processed_data["player_info"]["birth_province"]
                existing_player.birth_country = processed_data["player_info"]["birth_country"]
                existing_player.height_in_inches = processed_data["player_info"]["height_in_inches"]
                existing_player.weight_in_pounds = processed_data["player_info"]["weight_in_pounds"]
                existing_player.points_per_game = processed_data["career_stats"]["points_per_game"]
                existing_player.goals_per_game = processed_data["career_stats"]["goals_per_game"]
                existing_player.games_played = processed_data["career_stats"]["gamesPlayed"]
                existing_player.goals = processed_data["career_stats"]["goals"]
                existing_player.assists = processed_data["career_stats"]["assists"]
                existing_player.points = processed_data["career_stats"]["points"]
                existing_player.shots = processed_data["career_stats"]["shots"]
                existing_player.power_play_goals = processed_data["career_stats"]["powerPlayGoals"]
                existing_player.shooting_pct = processed_data["career_stats"]["shootingPctg"]
                existing_player.avg_toi = processed_data["career_stats"]["avgToi"]
                existing_player.team_id = processed_data["player_info"]["team_id"]
            else:
                # Insert a new player into the database
                new_player = Player(
                    player_id=player_id,
                    first_name=processed_data["player_info"]["first_name"],
                    last_name=processed_data["player_info"]["last_name"],
                    team_name=processed_data["player_info"]["team_name"],
                    position=processed_data["player_info"]["position"],
                    jersey_number=processed_data["player_info"]["jersey_number"],
                    headshot=processed_data["player_info"]["headshot"],
                    birth_city=processed_data["player_info"]["birth_city"],
                    birth_province=processed_data["player_info"]["birth_province"],
                    birth_country=processed_data["player_info"]["birth_country"],
                    height_in_inches=processed_data["player_info"]["height_in_inches"],
                    weight_in_pounds=processed_data["player_info"]["weight_in_pounds"],
                    points_per_game=processed_data["career_stats"]["points_per_game"],
                    goals_per_game=processed_data["career_stats"]["goals_per_game"],
                    games_played=processed_data["career_stats"]["gamesPlayed"],
                    goals=processed_data["career_stats"]["goals"],
                    assists=processed_data["career_stats"]["assists"],
                    points=processed_data["career_stats"]["points"],
                    shots=processed_data["career_stats"]["shots"],
                    power_play_goals=processed_data["career_stats"]["powerPlayGoals"],
                    shooting_pct=processed_data["career_stats"]["shootingPctg"],
                    avg_toi=processed_data["career_stats"]["avgToi"],
                    team_id=processed_data["player_info"]["team_id"]
                )
                db.session.add(new_player)

    # Commit changes to the database
    try:
        db.session.commit()
        print('Data saved successfully to {}'.format(os.getenv('SQLALCHEMY_DATABASE_URI')))
        db.session.close()
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        print(f"Error saving data: {e}")
        db.session.close()


if __name__ == '__main__':
    """
    Entry point for the script.

    Loads environment variables, initializes the Flask app, and fetches player data.
    """
    # Load environment variables
    load_dotenv('.env')

    # Initialize the Flask application
    config_name = os.getenv('CONFIG_NAME')
    app = create_app(config_name=config_name)

    # Run the data fetching logic within the app context
    with app.app_context():
        fetch_player_data()