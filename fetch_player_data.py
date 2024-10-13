from app import db, create_app
from app.models import Player
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance
import os

def fetch_and_store_player_data():
    player_ids = [8478402, 8477934, 8475786]  # Example player IDs
    
    for player_id in player_ids:
        player_data = get_nhl_player_stats(player_id)

        if player_data:
            processed_data = analyze_player_performance(player_data)

            # Check if the player already exists in the database
            existing_player = Player.query.filter_by(player_id=player_id).first()

            if existing_player:
                # Update the existing player
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
            else:
                # Insert a new player
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
                    avg_toi=processed_data["career_stats"]["avgToi"]
                )
                db.session.add(new_player)

    db.session.commit()

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name=config_name)

if __name__ == '__main__':
    with app.app_context():
        fetch_and_store_player_data()