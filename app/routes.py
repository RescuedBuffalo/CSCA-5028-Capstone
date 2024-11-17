from flask import Blueprint, render_template, request, redirect, url_for, Response
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance
from app.models import Player, GameLog
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Counter, Histogram
import time


# Create a blueprint for the routes
bp = Blueprint('main', __name__)
REQUEST_COUNT = Counter('app_requests_toal', 'Total number of requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency in seconds')
# Metric that maps the player_id to the number of times it was searched
PLAYER_SEARCH_COUNT = Counter('player_search_count', 'Number of times a player was searched', ['player_id'])

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
            # Redirect to the player_profile route using the blueprint's name
            return redirect(url_for('main.player_profile', player_id=player_id))
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
        return render_template('report.html', error_message='Player not found'), 404

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

    return render_template('report.html', player_info=player_info, game_logs=game_logs)

# Route to expose the metrics
@bp.route('/metrics')
def metrics():
    registry = CollectorRegistry()

    data = generate_latest(registry)
    return Response(data, content_type=CONTENT_TYPE_LATEST)

# Middleware to track metric data before requests occur
@bp.before_request
def before_request():
    REQUEST_COUNT.inc()
    request.start_time = time.time()

# Middleware to track metric data after requests occur
@bp.after_request
def after_request(response):
    latency = time.time() - request.start_time

    REQUEST_LATENCY.observe(latency)

    # Increment the player search count metric
    player_id = request.args.get('player_id')
    if player_id:
        PLAYER_SEARCH_COUNT.labels(player_id).inc()

    return response 