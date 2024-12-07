from app import create_app, db
from app.models import Player, GameLog, PlayerRank, Team, Roster
from dotenv import load_dotenv

def populate_test_db():
    load_dotenv()
    app = create_app('testing')

    with app.app_context():
        db.create_all()

        # Add test data
        player = Player(
            player_id=1,
            first_name="Test",
            last_name="Player",
            team_name="Test Team",
            position="Forward",
            jersey_number=99,
            headshot="test_headshot_url",
            birth_city="Test City",
            birth_province="Test Province",
            birth_country="Test Country",
            height_in_inches=72,
            weight_in_pounds=200,
            points_per_game=1.0,
            goals_per_game=0.5,
            avg_toi=20.0,
            shooting_pct=10.0,
            games_played=82,
            goals=41,
            assists=41,
            points=82,
            shots=410,
            power_play_goals=10,
            team_id = 9999
        )
        db.session.add(player)

        player2 = Player(
            player_id=2,
            first_name="Test2",
            last_name="Player2",
            team_name="Test Team",
            position="Forward",
            jersey_number=98,
            headshot="test_headshot_url2",
            birth_city="Test City",
            birth_province="Test Province",
            birth_country="Test Country",
            height_in_inches=72,
            weight_in_pounds=200,
            points_per_game=1.0,
            goals_per_game=0.5,
            avg_toi=20.0,
            shooting_pct=10.0,
            games_played=82,
            goals=41,
            assists=41,
            points=82,
            shots=410,
            power_play_goals=10,
            team_id = 9999
        )
        db.session.add(player2)

        game_log = GameLog(
            player_id=1,
            game_id=1,
            game_date="2024-12-01",
            opponent="Test Opponent",
            home_road_flag="H",
            goals=1,
            assists=2,
            points=3,
            shots=5,
            plus_minus=1,
            power_play_goals=1,
            pim=0,
            toi=20.5,
        )
        db.session.add(game_log)

        player_rank = PlayerRank(
            player_id=1,
            rank=0.99
        )
        db.session.add(player_rank)

        player_rank2 = PlayerRank(
            player_id=1,
            rank=0.01
        )
        db.session.add(player_rank2)

        team = Team(
            team_id=9999,
            franchise_id=9999,
            full_name="Test Team",
            raw_tricode="TST",
            tricode="TST",
            league_id=1
        )
        db.session.add(team)
        team2 = Team(
            team_id=99992,
            franchise_id=99992,
            full_name="Test Team2",
            raw_tricode="TST2",
            tricode="TST2",
            league_id=1
        )
        db.session.add(team2)

        roster = Roster(
            player_id=1,
            team_id=9999,
            season="20242025"
        )
        db.session.add(roster)

        roster2 = Roster(
            player_id=2,
            team_id=9999,
            season="20242025"
        )
        db.session.add(roster2)


        db.session.commit()

if __name__ == "__main__":
    populate_test_db()