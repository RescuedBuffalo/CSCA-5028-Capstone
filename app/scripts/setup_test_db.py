from app import create_app, db
from app.models import Player, GameLog, PlayerRank
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
        )
        db.session.add(player)

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
            rank=0.5
        )
        db.session.add(player_rank)

        db.session.commit()

if __name__ == "__main__":
    populate_test_db()