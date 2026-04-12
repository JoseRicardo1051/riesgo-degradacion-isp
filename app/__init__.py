import os

from dotenv import load_dotenv
from flask import Flask

from .extensions import db


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_db = os.getenv("MYSQL_DB", "isp_risk_db")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from . import models

        db.create_all()

    from .routes.api import api_bp
    from .routes.web import web_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app
