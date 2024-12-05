from flask import Blueprint, render_template, request, redirect, url_for, Response
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance
from app.models import Player, GameLog
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY, Counter, Histogram
import time
import os
import logging as LOGGER


# Create a blueprint for the routes
bp = Blueprint('main', __name__)
REQUEST_COUNT = Counter('app_requests_toal', 'Total number of requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency in seconds', buckets=[0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
# Metric that maps the player_id to the number of times it was searched
PLAYER_SEARCH_COUNT = Counter('player_search_count', 'Number of times a player was searched', ['player_id'])
ERROR_COUNT = Counter('app_request_error_count', 'Total number of errors in requests')
DATABASE_CONNECTIONS = Counter('database_connection_count', 'Number of times a connection to the database was made', ['database'])

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
            # Redirect to the player_profile route using the blueprint's name
            return redirect(url_for('main.player_profile', player_id=player_id))
        else:
            error_message = f'Could not fetch data with player ID: {player_id}'
            return render_template('index.html', error_message=error_message)

    # Render the form when the request method is GET
    return render_template('index.html')


# Route to display player profile from the database
@bp.route('/player/<int:player_id>', methods=['GET'])
def player_profile(player_id):
    try:
        PLAYER_SEARCH_COUNT.labels(player_id=player_id).inc()
        DATABASE_CONNECTIONS.labels(database=os.getenv('SQLALCHEMY_DATABASE_URI')).inc()
    except Exception as e:
        LOGGER.error(f"Error incrementing player search count: {e}")

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

@bp.route('/metrics')
def metrics():
    data = generate_latest(REGISTRY)
    return Response(data, content_type=CONTENT_TYPE_LATEST, status=200)

@bp.route('/health')
def health():
    return Response("ok", status=200)

@bp.before_request
def before_request():
    if request.endpoint == 'metrics':
        return
    
    REQUEST_COUNT.inc()
    request.start_time = time.time()

@bp.after_request
def after_request(response):
    if request.endpoint == 'metrics':
        return
    
    latency = time.time() - request.start_time

    REQUEST_LATENCY.observe(latency)

    if response.status_code == 404 and request.endpoint == 'main.player_profile':
        ERROR_COUNT.inc()

    return response 