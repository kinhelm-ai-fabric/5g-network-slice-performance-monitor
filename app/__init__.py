import os
import json
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app():
    app = Flask(__name__)

    # ── Security configuration ───────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    app.config["SESSION_COOKIE_NAME"] = "5g_slice_monitor_session"
    app.config["SESSION_COOKIE_PATH"] = os.environ.get("SESSION_COOKIE_PATH", "/")
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get(
        "SESSION_COOKIE_SECURE", "false"
    ).lower() in ("true", "1", "yes")
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # ── ProxyFix ─────────────────────────────────────────────────────
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # ── Logging ──────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ── Data directory ───────────────────────────────────────────────
    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    app.config["DATA_DIR"] = os.path.abspath(data_dir)

    # ── Kindo agent config ───────────────────────────────────────────
    app.config["KINDO_API_KEY"] = os.environ.get("KINDO_API_KEY", "")
    app.config["KINDO_SLICE_PERFORMANCE_AGENT_ID"] = os.environ.get(
        "KINDO_SLICE_PERFORMANCE_AGENT_ID", ""
    )

    # ── Initialize data store ────────────────────────────────────────
    from app.models.data_store import init_data_store
    init_data_store(app.config["DATA_DIR"])

    # ── Register blueprints ──────────────────────────────────────────
    from app.routes.main import main_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # ── Template context ─────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        return {"app_name": "5G Slice Monitor"}

    return app
