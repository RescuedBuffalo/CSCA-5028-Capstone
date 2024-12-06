from app import db, create_app
from app.models import Team
from app.utils.nhl_api import get_nhl_teams
import os
from dotenv import load_dotenv

load_dotenv('.env')
config_name = os.getenv('CONFIG_NAME')

app = create_app(config_name=config_name)

def fetch_team_data():
    with app.app_context():  # Create the application context
        teams = get_nhl_teams()['data']

        for team in teams:
            try:
                existing_team = Team.query.filter_by(team_id=team['id']).first()
            except Exception as e:
                existing_team = None
                print(f"Error querying Team table: {e}")

            if not existing_team:
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

        try:
            db.session.commit()
            print('Data saved successfully to {}'.format(os.getenv('SQLALCHEMY_DATABASE_URI')))
        except Exception as e:
            db.session.rollback()
            print(f"Error saving data: {e}")