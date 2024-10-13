from app import db

class Player(db.Model):
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

    def __repr__(self):
        return f'<Player {self.first_name} {self.last_name}>'