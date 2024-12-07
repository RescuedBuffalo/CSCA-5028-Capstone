from flask import Blueprint, render_template, request, redirect, url_for, Response
from app.utils.nhl_api import get_nhl_player_stats
from app.utils.analysis import analyze_player_performance
from app.models import Player, GameLog, PlayerRank, Roster, Team
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY, Counter, Histogram
import time
import os
import logging as LOGGER
import app.scripts.producer as producer
from sqlalchemy import text
from app import db


# Create a blueprint for the routes
bp = Blueprint('main', __name__)
REQUEST_COUNT = Counter('app_requests_toal', 'Total number of requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency in seconds', buckets=[0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
# Metric that maps the player_id to the number of times it was searched
PLAYER_SEARCH_COUNT = Counter('player_search_count', 'Number of times a player was searched', ['player_id'])
ERROR_COUNT = Counter('app_request_error_count', 'Total number of errors in requests')
DATABASE_CONNECTIONS = Counter('database_connection_count', 'Number of times a connection to the database was made', ['database'])
PRODUCER_TRIGGERED = Counter('producer_triggered_count', 'Number of times the producer was triggered')
PRODUCER_SUCCEEDED = Counter('producer_succeeded_count', 'Number of times the producer succeeded')

# Home route with a form to enter a player ID
@bp.route('/', methods=['GET'])
def index():
    try:
        teams = Team.query.all()
        DATABASE_CONNECTIONS.labels(database=os.getenv('SQLALCHEMY_DATABASE_URI')).inc()
        print(teams)
        return render_template('index.html', teams=teams), 200
    except Exception as e:
        LOGGER.error(f"Error fetching teams: {e}")
        return render_template('index.html', teams=None, error_message='Failed to fetch teams'), 404

@bp.route('/team/<int:team_id>', methods=['GET'])
def team_profile(team_id):
    try:
        # Extract player IDs as a flat list
        player_ids = [player_id for (player_id,) in db.session.query(Roster.player_id).filter_by(team_id=team_id).distinct().all()]
        
        # Query the players using the flat list of IDs
        roster_info = Player.query.filter(Player.player_id.in_(player_ids)).all()
        
        DATABASE_CONNECTIONS.labels(database=os.getenv('SQLALCHEMY_DATABASE_URI')).inc()
        return render_template('roster.html', roster=roster_info), 200
    
    except Exception as e:
        LOGGER.error(f"Error fetching team: {e}")
        return render_template('roster.html', roster=None, error_message='Team not found'), 404

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
    player_rank = PlayerRank.query.filter_by(player_id=player_id).first()

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
        "rank": player_rank.rank,
        "shots": player.shots,
        "power_play_goals": player.power_play_goals
    }

    return render_template('report.html', player_info=player_info, game_logs=game_logs)

@bp.route('/analyze/players', methods=['POST'])
def analyze_players():
    try:
        # Fetch all players and calculate percent rank
        players = Player.query.order_by(Player.points_per_game.desc()).all()
        total_players = len(players)

        # Drop the players_ranked table if it exists (for the sake of exercise)
        PlayerRank.query.delete()

        # Calculate percent rank and save it in the players_ranked table
        for idx, player in enumerate(players):
            percent_rank = idx / (total_players - 1) if total_players > 1 else 0
            player_rank = PlayerRank(
                player_id=player.player_id,
                rank=percent_rank
            )
            db.session.add(player_rank)

        db.session.commit()
        return Response("Players analysis completed.", status=200)
    except Exception as e:
        db.session.rollback()
        LOGGER.error(f"Error analyzing players: {e}")
        return Response(f"Failed to analyze players", status=500)

@bp.route('/produce_tasks', methods=['POST'])
def produce_tasks():
    response_code = producer.main()
    PRODUCER_TRIGGERED.inc()

    if response_code != 200:
        return Response("Failed to add tasks to queue.", status=response_code)
    else:
        PRODUCER_SUCCEEDED.inc()
        return Response("Tasks successfully added to queue.", status=response_code)

@bp.route('/metrics', methods=['POST'])
def metrics():
    data = generate_latest(REGISTRY)
    return Response(data, content_type=CONTENT_TYPE_LATEST, status=200)

@bp.route('/health', methods=['POST'])
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