"""
Script for fetching and saving NHL team roster data.

This script:
- Retrieves team information from the database.
- Fetches the roster for each team from the NHL API for a specified season.
- Updates or inserts roster data into the `Roster` database table, avoiding duplicates.

Dependencies:
- `requests` for making HTTP requests to the NHL API.
- `dotenv` for loading environment variables.
- Flask app and SQLAlchemy for database interactions.

Usage:
Run this script to fetch and save NHL team rosters for the current season.

Environment Variables:
- `CONFIG_NAME`: The Flask configuration name (e.g., development, production).
- `SQLALCHEMY_DATABASE_URI`: The database connection URI.

Example:
    python fetch_roster_data.py
"""

from app import db, create_app
from app.models import Roster, Team
from app.utils.nhl_api import get_nhl_team_roster_by_season
import os
from dotenv import load_dotenv


def fetch_roster_data():
    """
    Fetch and save NHL roster data for all teams.

    Steps:
    1. Query the `Team` table to get all teams in the database.
    2. Fetch the roster for each team from the NHL API for the specified season.
    3. Check if a player's roster entry for the current season already exists in the database.
    4. Insert new roster entries for players not already in the database.

    API Endpoint:
        - `get_nhl_team_roster_by_season(tricode, season)`
        - Parameters:
            - `tricode`: The team's tricode (e.g., "EDM" for Edmonton Oilers).
            - `season`: The NHL season in "YYYYYYYY" format (e.g., "20242025").

    Database Tables:
        - `Team`: Contains metadata about NHL teams.
        - `Roster`: Stores the player roster for each team by season.

    Raises:
        Exception: Rolls back the transaction if a database commit fails.
    """
    # Query all teams from the database
    teams = db.session.query(Team).all()

    for team in teams:
        # Fetch the roster for the given team and season
        roster = get_nhl_team_roster_by_season(team.tricode, '20242025')

        if not roster == '404':  # Skip if the API returns a "404 Not Found" response
            # Process forwards
            for forward in roster['forwards']:
                existing_forward = Roster.query.filter_by(player_id=forward['id'], team_id=team.team_id, season='20242025').first()
                if not existing_forward:
                    new_forward = Roster(
                        player_id=forward['id'],
                        team_id=team.team_id,
                        season='20242025',
                    )
                    db.session.add(new_forward)

            # Process defensemen
            for defenseman in roster['defensemen']:
                existing_defenseman = Roster.query.filter_by(player_id=defenseman['id'], team_id=team.team_id, season='20242025').first()
                if not existing_defenseman:
                    new_defenseman = Roster(
                        player_id=defenseman['id'],
                        team_id=team.team_id,
                        season='20242025',
                    )
                    db.session.add(new_defenseman)

            # Uncomment to include goalies when needed
            # for goalie in roster['goalies']:
            #     existing_goalie = Roster.query.filter_by(player_id=goalie['id'], team_id=team.team_id, season='20242025').first()
            #     if not existing_goalie:
            #         new_goalie = Roster(
            #             player_id=goalie['id'],
            #             team_id=team.team_id,
            #             season='20242025',
            #         )
            #         db.session.add(new_goalie)

    # Commit the changes to the database
    try:
        db.session.commit()
        print('Data saved successfully to {}'.format(os.getenv('SQLALCHEMY_DATABASE_URI')))
        db.session.close()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving data: {e}")
        db.session.close()


# Load environment variables
load_dotenv('.env')
print('CONFIG: ', os.getenv('CONFIG_NAME'))
config_name = os.getenv('CONFIG_NAME')

# Create the Flask app instance using the environment configuration
app = create_app(config_name=config_name)

if __name__ == '__main__':
    """
    Entry point for the script.

    Ensures the Flask app context is initialized before running the data fetching function.
    This is required for database operations as they rely on the Flask app context.

    Steps:
    1. Load the app context using `app.app_context()`.
    2. Call `fetch_roster_data()` to fetch and store roster data in the database.
    """
    with app.app_context():
        fetch_roster_data()