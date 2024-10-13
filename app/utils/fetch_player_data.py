from app import db
from app.models import Player
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance

def fetch_and_store_player_data():
    # List of player IDs to fetch (replace with all player IDs)
    player_ids = [8478402, 8477934, 8475786]  # Add all relevant player IDs here
    
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
                existing_player.points_per_game = processed_data["career_stats"]["points_per_game"]
                existing_player.games_played = processed_data["career_stats"]["gamesPlayed"]
                existing_player.goals = processed_data["career_stats"]["goals"]
                existing_player.assists = processed_data["career_stats"]["assists"]
                existing_player.points = processed_data["career_stats"]["points"]
            else:
                # Insert a new player
                new_player = Player(
                    player_id=player_id,
                    first_name=processed_data["player_info"]["first_name"],
                    last_name=processed_data["player_info"]["last_name"],
                    team_name=processed_data["player_info"]["team_name"],
                    position=processed_data["player_info"]["position"],
                    points_per_game=processed_data["career_stats"]["points_per_game"],
                    games_played=processed_data["career_stats"]["gamesPlayed"],
                    goals=processed_data["career_stats"]["goals"],
                    assists=processed_data["career_stats"]["assists"],
                    points=processed_data["career_stats"]["points"]
                )
                db.session.add(new_player)

    # Commit all changes to the database
    db.session.commit()

if __name__ == "__main__":
    fetch_and_store_player_data()