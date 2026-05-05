from flask import Flask, redirect, session, url_for

from config import Config
from models.db import close_db, init_db
from routes.analytics import analytics_bp
from routes.auth import auth_bp
from routes.expenses import expenses_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.teardown_appcontext(close_db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(analytics_bp)

    init_db(app)

    @app.route("/")
    def home():
        if session.get("user_id"):
            return redirect(url_for("analytics.dashboard"))
        return redirect(url_for("auth.title_screen"))

    @app.context_processor
    def inject_globals():
        return {
            "logged_in": bool(session.get("user_id")),
            "current_user": session.get("username"),
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
