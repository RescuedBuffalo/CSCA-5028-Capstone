from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize the database and migration tool (no app attached yet)
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Initialize the Flask app
    app = Flask(__name__)

    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database and migration tool with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import your routes here to avoid circular imports
    from app import routes

    return app