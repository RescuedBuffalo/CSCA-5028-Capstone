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

# Prometheus metrics for monitoring
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency in seconds', buckets=[0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
PLAYER_SEARCH_COUNT = Counter('player_search_count', 'Number of times a player was searched', ['player_id'])
ERROR_COUNT = Counter('app_request_error_count', 'Total number of errors in requests')
DATABASE_CONNECTIONS = Counter('database_connection_count', 'Number of times a connection to the database was made', ['database'])
PRODUCER_TRIGGERED = Counter('producer_triggered_count', 'Number of times the producer was triggered')
PRODUCER_SUCCEEDED = Counter('producer_succeeded_count', 'Number of times the producer succeeded')

# Routes

@bp.route('/', methods=['GET'])
def index():
    """
    Home page displaying a list of all NHL teams.
    Fetches teams from the database and orders them alphabetically by full name.
    """
    try:
        # Ensure the Team table exists
        if not db.inspect(db.engine).has_table("team"):
            LOGGER.warning("The 'team' table does not exist in the database.")
            return render_template('index.html', teams=None, error_message="The team table is missing from the database."), 500

        teams = Team.query.order_by(Team.full_name.asc()).all()
        DATABASE_CONNECTIONS.labels(database=os.getenv('SQLALCHEMY_DATABASE_URI')).inc()

        if not teams:
            LOGGER.warning("No teams found in the database.")
            return render_template('index.html', teams=None, error_message="No teams found in the database."), 404

        return render_template('index.html', teams=teams), 200

    except Exception as e:
        LOGGER.error(f"Error fetching teams: {e}")
        return render_template('index.html', teams=None, error_message="Failed to fetch teams due to an internal error."), 500
    
@bp.route('/team/<int:team_id>', methods=['GET'])
def team_profile(team_id):
    """
    Team profile page displaying the roster of players for a specific team.
    Fetches player information for the specified team ID.
    """
    try:
        if not db.inspect(db.engine).has_table("team"):
            LOGGER.warning("The 'team' table does not exist in the database.")
            return render_template('roster.html', roster=None, error_message="The team table is missing from the database."), 500

        team = Team.query.filter_by(team_id=team_id).first()
        if not team:
            LOGGER.warning(f"Team ID {team_id} not found in the database.")
            return render_template('roster.html', roster=None, error_message="Team not found."), 404

        player_ids = [player_id for (player_id,) in db.session.query(Roster.player_id).filter_by(team_id=team_id).distinct().all()]

        if not player_ids:
            LOGGER.warning(f"No players found for team ID {team_id}.")
            return render_template('roster.html', roster=None, error_message="No players found for this team."), 404

        roster_info = Player.query.filter(Player.player_id.in_(player_ids)).order_by(Player.last_name.asc()).all()

        if not roster_info:
            LOGGER.warning(f"Roster data not available for team ID {team_id}.")
            return render_template('roster.html', roster=None, error_message="Roster data not available for this team."), 404

        DATABASE_CONNECTIONS.labels(database=os.getenv('SQLALCHEMY_DATABASE_URI')).inc()
        return render_template('roster.html', roster=roster_info), 200

    except Exception as e:
        LOGGER.error(f"Error fetching team profile for team ID {team_id}: {e}")
        return render_template('roster.html', roster=None, error_message="Error fetching team profile."), 500

@bp.route('/player/<int:player_id>', methods=['GET'])
def player_profile(player_id):
    """
    Player profile page displaying detailed information and performance logs.
    Includes career stats, percentile rank, and recent game performance.
    """
    try:
        PLAYER_SEARCH_COUNT.labels(player_id=player_id).inc()
        DATABASE_CONNECTIONS.labels(database=os.getenv('SQLALCHEMY_DATABASE_URI')).inc()

        player = Player.query.filter_by(player_id=player_id).first()

        if not player:
            LOGGER.warning(f"Player ID {player_id} not found in the database.")
            return render_template('report.html', error_message="Player not found."), 404

        game_logs = GameLog.query.filter_by(player_id=player_id).all()
        player_rank = PlayerRank.query.filter_by(player_id=player_id).first()

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
            "rank": player_rank.rank if player_rank else "N/A",
            "shots": player.shots,
            "power_play_goals": player.power_play_goals
        }

        return render_template('report.html', player_info=player_info, game_logs=game_logs, rank=player_rank), 200
    except Exception as e:
        LOGGER.error(f"Error fetching player profile for player ID {player_id}: {e}")
        return render_template('report.html', error_message="Error fetching player profile."), 500


@bp.route('/analyze/players', methods=['POST'])
def analyze_players():
    """
    Analyze player performance by calculating percentile ranks.
    Saves the calculated rank into the PlayerRank table.
    """
    try:
        players = Player.query.order_by(Player.points.asc()).all()

        if not players:
            LOGGER.warning("No players found in the database for analysis.")
            return Response("No players available for analysis.", status=404)

        total_players = len(players)

        PlayerRank.query.delete()  # Drop existing player ranks

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
        return Response("Failed to analyze players due to an internal error.", status=500)

@bp.route('/produce_tasks', methods=['POST'])
def produce_tasks():
    """
    Trigger the producer to add tasks to a queue.

    Returns:
        Response: Success or failure message with appropriate status code.
    """
    try:
        connection, channel = producer.connect_to_rabbitmq()  # Establish connection and channel
        task_sequence = ['fetch_team_data', 'fetch_roster_data', 'fetch_player_data', 'fetch_game_data']

        for task in task_sequence:
            producer.publish_task(task, channel)

        # Close the connection gracefully
        channel.close()
        connection.close()

        print("All tasks published successfully.")
        return Response("Tasks successfully added to queue.", status=200)
    except Exception as e:
        LOGGER.error(f"Failed to publish tasks: {e}")
        return Response("Failed to add tasks to queue.", status=500)

@bp.route('/metrics', methods=['POST'])
def metrics():
    """
    Return Prometheus metrics for the application.
    """
    data = generate_latest(REGISTRY)
    return Response(data, content_type=CONTENT_TYPE_LATEST, status=200)

@bp.route('/health', methods=['POST'])
def health():
    """
    Return a simple health check response.
    """
    return Response("ok", status=200)

# Middleware

@bp.before_request
def before_request():
    """
    Middleware to track request counts and start time for latency measurement.
    Skips the metrics endpoint.
    """
    if request.endpoint == 'metrics':
        return
    
    REQUEST_COUNT.inc()
    request.start_time = time.time()

@bp.after_request
def after_request(response):
    """
    Middleware to track request latency and log errors for specific endpoints.
    Skips the metrics endpoint.
    """
    if request.endpoint == 'metrics':
        return
    
    latency = time.time() - request.start_time
    REQUEST_LATENCY.observe(latency)

    if response.status_code == 404 and request.endpoint == 'main.player_profile':
        ERROR_COUNT.inc()

    return response