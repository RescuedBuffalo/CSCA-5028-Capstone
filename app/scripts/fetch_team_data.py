from app import db, create_app
from app.models import Team
from app.utils.nhl_api import get_nhl_teams
import os
from dotenv import load_dotenv


def fetch_team_data():
    teams = get_nhl_teams()['data']

    for team in teams:
        existing_team = Team.query.filter_by(team_id=team['id']).first()

        if not existing_team:
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
        db.session.close()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving data: {e}")
        db.session.close()

load_dotenv('.env')
print('CONFIG: ', os.getenv('CONFIG_NAME'))
config_name = os.getenv('CONFIG_NAME')

app = create_app(config_name=config_name)

if __name__ == '__main__':
    with app.app_context():
        fetch_team_data()