import requests
from app import db
from app.models import Player, GameLog

def fetch_player_game_logs():
    players = Player.query.all()
    season = "20242025"  # You can set the current season dynamically if needed
    sub_season = "2"  # 2 for regular season, 3 for playoffs

    for player in players:
        game_log_url = f'https://api-web.nhle.com/v1/player/{player.player_id}/game-log/{season}/{sub_season}'
        response = requests.get(game_log_url)

        if response.status_code == 200:
            game_logs = response.json().get('gameLog', [])

            for game in game_logs:
                # Check if the game log already exists
                existing_log = GameLog.query.filter_by(player_id=player.player_id, game_id=game['gameId']).first()

                if not existing_log:
                    new_game_log = GameLog(
                        player_id=player.player_id,
                        game_id=game['gameId'],
                        game_date=game['gameDate'],
                        opponent=game.get('opponentCommonName', {}).get('default', ''),
                        home_road_flag=game['homeRoadFlag'],
                        goals=game['goals'],
                        assists=game['assists'],
                        points=game['points'],
                        shots=game['shots'],
                        plus_minus=game['plusMinus'],
                        power_play_goals=game['powerPlayGoals'],
                        pim=game['pim'],
                        toi=game['toi']
                    )
                    db.session.add(new_game_log)
        else:
            print(f"Failed to fetch game logs for player {player.player_id}. Status Code: {response.status_code}")

    db.session.commit()

if __name__ == '__main__':
    fetch_player_game_logs()