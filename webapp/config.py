# Settings
# Every setting comes from an environment variable so the same code can run on my
# laptop, in the tests, or on a server without changing any files. If a variable
# is not set, a safe default for local use is used instead.

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_settings():
    instance = ROOT / "instance"
    return {
        # Where the SQLite database file is saved
        "DATABASE": os.environ.get("CAPSTONE_DB_PATH", str(instance / "capstone.db")),
        # Folder with the screenshots used in the questions (kept out of Git)
        "SCREENSHOT_DIR": os.environ.get("CAPSTONE_SCREENSHOT_DIR", str(instance / "screenshots")),
        # Used by Flask to sign session data. Must be changed on a real server.
        "SECRET_KEY": os.environ.get("CAPSTONE_SECRET_KEY", "change-me-for-local-use-only"),
        # Debug mode stays off unless it is turned on
        "DEBUG": os.environ.get("CAPSTONE_DEBUG", "0") == "1",
        "PORT": int(os.environ.get("PORT", "5000")),
        # Password for the researcher dashboard. If it is empty, the dashboard only
        # opens on this computer. It must be set on a real server (added in Unit 7).
        "ADMIN_PASSWORD": os.environ.get("CAPSTONE_ADMIN_PASSWORD", ""),
        # Question bank and training lesson that are loaded when the app starts
        "QUESTIONS_FILE": str(ROOT / "assessments" / "questions.json"),
        "LESSON_FILE": str(ROOT / "content" / "training-lesson.md"),
    }
