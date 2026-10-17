"""
Setup for the system tests.

The system tests start the real app on this computer and use a real browser
(Chromium, through Playwright) to click through the pages the same way a
participant would. If Playwright is not installed, these tests are skipped and
the other tests still run.

Set CAPSTONE_EVIDENCE_DIR to a folder to save a screenshot of each step.
"""

import os
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

playwright_api = pytest.importorskip("playwright.sync_api")

from werkzeug.serving import make_server  # noqa: E402

from webapp import create_app  # noqa: E402


@pytest.fixture
def live_app(tmp_path):
    # Fresh database for every test, real screenshots folder if it exists
    shots = ROOT / "instance" / "screenshots"
    app = create_app({
        "DATABASE": str(tmp_path / "system.db"),
        "SCREENSHOT_DIR": str(shots if shots.exists() else tmp_path),
    })
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", app
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    with playwright_api.sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1100, "height": 900})
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def evidence(request):
    # Save a screenshot when CAPSTONE_EVIDENCE_DIR is set, otherwise do nothing
    folder = os.environ.get("CAPSTONE_EVIDENCE_DIR")

    def save(page, name, full_page=False, locator=None):
        if not folder:
            return
        Path(folder).mkdir(parents=True, exist_ok=True)
        path = Path(folder) / f"{request.node.name}-{name}.png"
        if locator is not None:
            locator.screenshot(path=str(path))
        else:
            page.screenshot(path=str(path), full_page=full_page)

    return save
