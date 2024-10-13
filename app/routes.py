from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance
from app.models import Player

# Create a blueprint for the routes
bp = Blueprint('main', __name__)

# Home route with a form to enter a player ID
@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_id = request.form.get('player_id')

        if not player_id:
            return render_template('index.html', error_message='Please provide a player ID.')

        # Fetch player data using the NHL API
        player_data = get_nhl_player_stats(player_id)

        if player_data:
            analyzed_data = analyze_player_performance(player_data)
            return redirect(url_for('player_profile', player_id=player_id))
        else:
            error_message = f'Could not fetch data with player ID: {player_id}'
            return render_template('index.html', error_message=error_message)

    # Render the form when the request method is GET
    return render_template('index.html')


# Route to display player profile from the database
@bp.route('/player/<int:player_id>')
def player_profile(player_id):
    player = Player.query.filter_by(player_id=player_id).first()
    game_logs = GameLog.query.filter_by(player_id=player_id).all()

    if not player:
        return render_template('player_profile.html', error_message='Player not found'), 404

    # Prepare the player information and game logs
    player_info = {
        "first_name": player.first_name,
        "last_name": player.last_name,
        "team_name": player.team_name,
        "position": player.position,
        "jersey_number": player.jersey_number,
        "headshot": player.headshot,
        "birth_city": player.birth_city,
        "birth_province": player.birth_province,
        "birth_country": player.birth_country,
        "height_in_inches": player.height_in_inches,
        "weight_in_pounds": player.weight_in_pounds,
        "points_per_game": player.points_per_game,
        "goals_per_game": player.goals_per_game,
        "avg_toi": player.avg_toi,
        "shooting_pct": player.shooting_pct,
        "games_played": player.games_played,
        "goals": player.goals,
        "assists": player.assists,
        "points": player.points,
        "shots": player.shots,
        "power_play_goals": player.power_play_goals
    }

    return render_template('player_profile.html', player_info=player_info, game_logs=game_logs)