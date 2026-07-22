import logging
import os

from flask import Flask, redirect, url_for

from app.config import Config
from app.extensions import db


def create_app(config_class=Config):
    """Application factory: cria e configura a instância do Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    _configure_logging(app)

    db.init_app(app)

    from app.auth.routes import bp as auth_bp
    from app.agenda.routes import bp as agenda_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(agenda_bp)

    @app.route("/")
    def root():
        return redirect(url_for("agenda.index"))

    return app


def _configure_logging(app):
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app.logger.setLevel(log_level)
