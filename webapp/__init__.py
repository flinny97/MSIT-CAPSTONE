# Phishing awareness training web app
# This puts the four modules together:
#   M1 training delivery  -> pages.py (training lesson page)
#   M2 assessments        -> pages.py and api.py (pre and post tests)
#   M3 data storage       -> db.py (SQLite)
#   M4 scoring            -> scoring_bridge.py -> src/scoring/metrics.py

import re
import time

from flask import Flask, g, request

from .config import load_settings
from .db import close_db, get_db, init_db, now


def create_app(overrides=None):
    # Load the settings. The tests use overrides to point at a test database.
    app = Flask(__name__)
    app.config.update(load_settings())
    if overrides:
        app.config.update(overrides)

    # Set up the database and close it after each request
    init_db(app.config["DATABASE"], app.config["QUESTIONS_FILE"])
    app.teardown_appcontext(close_db)

    # Start a timer when a request comes in
    @app.before_request
    def start_timer():
        g.started = time.perf_counter()

    # Save how long each API call took. This is the latency data for the evaluation.
    @app.after_request
    def log_api_time(response):
        if request.path.startswith("/api/") and request.path != "/api/metrics/performance":
            ms = (time.perf_counter() - g.started) * 1000

            # Group routes like /api/tests/pre/questions under one name
            path = re.sub(r"/api/tests/(pre|post)/", "/api/tests/<test>/", request.path)

            db = get_db()
            db.execute(
                "INSERT INTO request_log VALUES (?, ?, ?, ?, ?)",
                (path, request.method, response.status_code, round(ms, 3), now())
            )
            db.commit()
        return response

    # Add the API routes and the page routes
    from .api import api
    from .pages import pages
    app.register_blueprint(api)
    app.register_blueprint(pages)
    return app
