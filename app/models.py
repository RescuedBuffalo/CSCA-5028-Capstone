from app import db

class Player(db.Model):
    """
    Represents a player in the NHL.

    Attributes:
        player_id (int): Unique ID for the player.
        first_name (str): First name of the player.
        last_name (str): Last name of the player.
        team_name (str): Name of the team the player belongs to.
        position (str): Player's position (e.g., Forward, Defenseman).
        jersey_number (int): Player's jersey number.
        headshot (str): URL to the player's headshot image.
        birth_city (str): City where the player was born.
        birth_province (str): Province where the player was born.
        birth_country (str): Country where the player was born.
        height_in_inches (int): Player's height in inches.
        weight_in_pounds (int): Player's weight in pounds.
        points_per_game (float): Average points per game.
        goals_per_game (float): Average goals per game.
        games_played (int): Total number of games played.
        goals (int): Total goals scored.
        assists (int): Total assists made.
        points (int): Total points earned.
        shots (int): Total number of shots taken.
        power_play_goals (int): Goals scored during power plays.
        shooting_pct (float): Shooting percentage.
        avg_toi (str): Average time on ice per game.
        team_id (int): ID of the team the player belongs to.
    """
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    jersey_number = db.Column(db.Integer, nullable=False)
    headshot = db.Column(db.String(255), nullable=False)
    birth_city = db.Column(db.String(100), nullable=False)
    birth_province = db.Column(db.String(100), nullable=False)
    birth_country = db.Column(db.String(100), nullable=False)
    height_in_inches = db.Column(db.Integer, nullable=False)
    weight_in_pounds = db.Column(db.Integer, nullable=False)
    points_per_game = db.Column(db.Float, nullable=False)
    goals_per_game = db.Column(db.Float, nullable=False)
    games_played = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.Integer, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    shots = db.Column(db.Integer, nullable=False)
    power_play_goals = db.Column(db.Integer, nullable=False)
    shooting_pct = db.Column(db.Float, nullable=False)
    avg_toi = db.Column(db.String(10), nullable=False)
    team_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        """
        Converts the Player object to a dictionary for JSON serialization.
        """
        return {
            'player_id': self.player_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'team_name': self.team_name,
            'position': self.position,
            'jersey_number': self.jersey_number,
            'headshot': self.headshot,
            'birth_city': self.birth_city,
            'birth_province': self.birth_province,
            'birth_country': self.birth_country,
            'height_in_inches': self.height_in_inches,
            'weight_in_pounds': self.weight_in_pounds,
            'points_per_game': self.points_per_game,
            'goals_per_game': self.goals_per_game,
            'games_played': self.games_played,
            'goals': self.goals,
            'assists': self.assists,
            'points': self.points,
            'shots': self.shots,
            'power_play_goals': self.power_play_goals,
            'shooting_pct': self.shooting_pct,
            'avg_toi': self.avg_toi
        }

    def __repr__(self):
        """
        Provides a string representation of the Player object.
        """
        return f'<Player {self.first_name} {self.last_name}>'


class GameLog(db.Model):
    """
    Represents a single game log for a player.

    Attributes:
        player_id (int): ID of the player associated with this game log.
        game_id (int): Unique ID of the game.
        game_date (str): Date of the game.
        opponent (str): Opponent team.
        home_road_flag (str): Indicates if the game was at home ('H') or away ('R').
        goals (int): Goals scored in the game.
        assists (int): Assists made in the game.
        points (int): Total points earned in the game.
        shots (int): Total number of shots taken.
        plus_minus (int): Plus/minus rating for the game.
        power_play_goals (int): Power play goals scored.
        pim (int): Penalty minutes in the game.
        toi (str): Time on ice during the game.
    """
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    game_date = db.Column(db.String(20), nullable=False)
    opponent = db.Column(db.String(50), nullable=False)
    home_road_flag = db.Column(db.String(1), nullable=False)
    goals = db.Column(db.Integer, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    shots = db.Column(db.Integer, nullable=False)
    plus_minus = db.Column(db.Integer, nullable=False)
    power_play_goals = db.Column(db.Integer, nullable=False)
    pim = db.Column(db.Integer, nullable=False)
    toi = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        """
        Converts the GameLog object to a dictionary for JSON serialization.
        """
        return {
            'player_id': self.player_id,
            'game_id': self.game_id,
            'game_date': self.game_date,
            'opponent': self.opponent,
            'home_road_flag': self.home_road_flag,
            'goals': self.goals,
            'assists': self.assists,
            'points': self.points,
            'shots': self.shots,
            'plus_minus': self.plus_minus,
            'power_play_goals': self.power_play_goals,
            'pim': self.pim,
            'toi': self.toi
        }

    def __repr__(self):
        """
        Provides a string representation of the GameLog object.
        """
        return f'<GameLog {self.player_id} - {self.game_date}>'


class Team(db.Model):
    """
    Represents an NHL team.

    Attributes:
        team_id (int): Unique ID for the team.
        franchise_id (int): Franchise ID of the team.
        full_name (str): Full name of the team.
        raw_tricode (str): Raw tricode representation of the team.
        tricode (str): Official tricode of the team.
        league_id (int): League ID of the team.
    """
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, unique=True, nullable=False)
    franchise_id = db.Column(db.Integer, nullable=True)
    full_name = db.Column(db.String(100), nullable=False)
    raw_tricode = db.Column(db.String(3), nullable=False)
    tricode = db.Column(db.String(3), nullable=False)
    league_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        """
        Converts the Team object to a dictionary for JSON serialization.
        """
        return {
            'team_id': self.team_id,
            'franchise_id': self.franchise_id,
            'full_name': self.full_name,
            'raw_tricode': self.raw_tricode,
            'tricode': self.tricode,
            'league_id': self.league_id
        }

    def __repr__(self):
        """
        Provides a string representation of the Team object.
        """
        return f'<Team {self.full_name}>'

class Roster(db.Model):
    """
    Represents the roster of a team for a specific season.

    Attributes:
        player_id (int): ID of the player in the roster.
        team_id (int): ID of the team in the roster.
        season (str): Season associated with the roster.
    """
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, nullable=False)
    season = db.Column(db.String(8), nullable=False)

    def to_dict(self):
        """
        Converts the Roster object to a dictionary for JSON serialization.
        """
        return {
            'player_id': self.player_id,
            'team_id': self.team_id,
            'season': self.season
        }

    def __repr__(self):
        """
        Provides a string representation of the Roster object.
        """
        return f'<Roster Player {self.player_id} Team {self.team_id}>'

class PlayerRank(db.Model):
    """
    Represents the percentile rank of a player based on performance metrics.

    Attributes:
        player_id (int): ID of the player.
        rank (float): Percentile rank of the player.
    """
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Float, nullable=False)

    def to_dict(self):
        """
        Converts the PlayerRank object to a dictionary for JSON serialization.
        """
        return {
            'player_id': self.player_id,
            'rank': self.rank
        }

    def __repr__(self):
        """
        Provides a string representation of the PlayerRank object.
        """
        return f'<PlayerRank Player {self.player_id} Rank {self.rank}>'