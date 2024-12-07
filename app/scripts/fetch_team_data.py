"""
Script for fetching and saving NHL team data.

This script:
- Retrieves a list of NHL teams from an external API.
- Checks if each team has stats available before saving them to the database.
- Updates the `Team` database table by adding new teams if they don't already exist.

Dependencies:
- `requests` (via `get_nhl_teams`) for interacting with the NHL API.
- `dotenv` for loading environment variables.
- Flask app and SQLAlchemy for database interactions.

Usage:
Run this script to fetch and store NHL team data in the database.

Environment Variables:
- `CONFIG_NAME`: The Flask configuration name (e.g., development, production).
- `SQLALCHEMY_DATABASE_URI`: The database connection URI.

Example:
    python fetch_team_data.py
"""

from app import db, create_app
from app.models import Team
from app.utils.nhl_api import get_nhl_teams, check_team_has_stats
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv('.env')
config_name = os.getenv('CONFIG_NAME')

# Create the Flask application
app = create_app(config_name=config_name)

def fetch_team_data():
    """
    Fetch and save NHL team data to the database.

    Steps:
    1. Retrieve a list of NHL teams from the NHL API.
    2. Check if each team already exists in the `Team` table.
    3. If a team does not exist and has stats available, add it to the `Team` table.
    4. Commit all changes to the database.

    External Dependencies:
    - `get_nhl_teams`: Fetches all NHL teams from the NHL API.
    - `check_team_has_stats`: Validates if a team has stats available based on its tricode.

    Database Tables:
        - `Team`: Stores metadata about NHL teams.

    Raises:
        Exception: Rolls back the transaction if database commit fails.

    Example:
        fetch_team_data()
    """
    with app.app_context():  # Create the application context
        # Fetch teams from the NHL API
        teams = get_nhl_teams()['data']

        for team in teams:
            try:
                # Check if the team already exists in the database
                existing_team = Team.query.filter_by(team_id=team['id']).first()
            except Exception as e:
                existing_team = None
                print(f"Error querying Team table: {e}")

            # Add the team if it does not exist and has stats available
            if not existing_team and check_team_has_stats(team['triCode']):
                print('Adding new team...')
                new_team = Team(
                    team_id=team['id'],
                    franchise_id=team['franchiseId'],
                    full_name=team['fullName'],
                    raw_tricode=team['rawTricode'],
                    tricode=team['triCode'],
                    league_id=team['leagueId']
                )
                db.session.add(new_team)

        # Commit the changes to the database
        try:
            db.session.commit()
            print('Data saved successfully to {}'.format(os.getenv('SQLALCHEMY_DATABASE_URI')))
        except Exception as e:
            # Rollback in case of an error
            db.session.rollback()
            print(f"Error saving data: {e}")

if __name__ == '__main__':
    """
    Entry point for the script.

    Ensures the Flask application context is initialized before running the data fetching function.
    This is required for database interactions as they rely on the Flask app context.
    """
    with app.app_context():
        fetch_team_data()