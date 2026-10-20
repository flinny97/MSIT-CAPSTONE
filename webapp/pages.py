# Pages layer
# These routes only send the HTML pages. Each page uses JavaScript (static/app.js)
# to call the API, so all reading and saving of data goes through api.py.

import html
import re
from pathlib import Path

from flask import Blueprint, abort, current_app, render_template, send_from_directory

pages = Blueprint("pages", __name__)


def lesson_html():
    # Read the training lesson from the lesson file
    text = Path(current_app.config["LESSON_FILE"]).read_text(encoding="utf-8")
    out = []
    in_list = False

    # Change each line of the lesson into HTML
    for line in text.splitlines():
        line = line.rstrip()

        # Show the text as plain text and make **words** bold
        safe = html.escape(line)
        safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)

        # Lines that start with "- " are bullet points
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{safe[2:]}</li>")
            continue

        # Close the list when the bullet points end
        if in_list:
            out.append("</ul>")
            in_list = False

        # Headings and normal paragraphs
        if line.startswith("## "):
            out.append(f"<h2>{safe[3:]}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{safe[2:]}</h1>")
        elif line != "":
            out.append(f"<p>{safe}</p>")

    # Close the list if the lesson ends with bullet points
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


@pages.get("/")
def consent():
    # First page: consent form and participant ID
    return render_template("consent.html")


@pages.get("/test/<test>")
def test_page(test):
    # Pre-assessment or post-assessment page
    if test not in ("pre", "post"):
        abort(404)
    title = "Pre-Assessment" if test == "pre" else "Post-Assessment"
    return render_template("test.html", test=test, title=title)


@pages.get("/training")
def training():
    # Training lesson page
    return render_template("training.html", lesson=lesson_html())


@pages.get("/feedback")
def feedback():
    # Feedback form after the post-assessment
    return render_template("feedback.html")


@pages.get("/admin")
def admin():
    # Researcher dashboard
    return render_template("admin.html")


@pages.get("/screenshots/<path:name>")
def screenshot(name):
    # Screenshots for the questions are kept in a local folder, not in the repository
    return send_from_directory(current_app.config["SCREENSHOT_DIR"], name)
