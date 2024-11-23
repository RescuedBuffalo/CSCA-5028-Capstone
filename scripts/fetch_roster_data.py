from app import db, create_app
from app.models import Roster, Team
from app.utils.nhl_api import get_nhl_team_roster_by_season
import os
from dotenv import load_dotenv


def fetch_roster_data():
    teams = db.session.query(Team).all()

    for team in teams:

        roster = get_nhl_team_roster_by_season(team.tricode, '20242025')

        if not roster == '404':
            for forward in roster['forwards']:
                existing_forward = Roster.query.filter_by(player_id=forward['id'], team_id=team.team_id, season='20242025').first()

                if not existing_forward:
                    new_forward = Roster(
                        player_id=forward['id'],
                        team_id=team.team_id,
                        season='20242025',
                    )
                    db.session.add(new_forward)
            for defenseman in roster['defensemen']:
                existing_defenseman = Roster.query.filter_by(player_id=defenseman['id'], team_id=team.team_id, season='20242025').first()

                if not existing_defenseman:
                    new_defenseman = Roster(
                        player_id=defenseman['id'],
                        team_id=team.team_id,
                        season='20242025',
                    )
                    db.session.add(new_defenseman)
            
            # for goalie in roster['goalies']:
            #     existing_goalie = Roster.query.filter_by(player_id=goalie['id'], team_id=team.team_id, season='20242025').first()

            #     if not existing_goalie:
            #         new_goalie = Roster(
            #             player_id=goalie['id'],
            #             team_id=team.team_id,
            #             season='20242025',
            #         )
            #         db.session.add(new_goalie)

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
        fetch_roster_data()