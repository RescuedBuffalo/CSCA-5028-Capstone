from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config 
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import CollectorRegistry, REGISTRY

db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)

    # Apply the configuration to the app based on the passed config name
    if config_name:
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config['default'])  # Fallback to default config

    db.init_app(app)
    Migrate(app, db)

    # Avoid duplicating metrics
    if not any(m.name == 'app_info' for m in REGISTRY.collect()):
        metrics = PrometheusMetrics(app)
        metrics.info('app_info', 'Application info', version='1.0.0')

    from app.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
