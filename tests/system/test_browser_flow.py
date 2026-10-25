"""
System tests for Unit 7.

These run the complete app in a real browser and follow the same steps a
participant would: consent, pre-assessment, training lesson, post-assessment,
and feedback. The researcher dashboard is then checked for the result.
Only synthetic participant IDs are used.
"""

from webapp.db import get_db


def answer_key(app, test):
    with app.app_context():
        return {r["item_id"]: r["answer"] for r in get_db().execute(
            "SELECT item_id, answer FROM questions WHERE test = ?", (test,))}


def answer(page, item, choice=None, confidence=None):
    if choice:
        page.check(f'input[name="{item}"][value="{choice}"]')
    if confidence:
        page.check(f'input[name="{item}-conf"][value="{confidence}"]')


def answer_all(page, key, skip=()):
    for item, right in key.items():
        if item not in skip:
            answer(page, item, right, 4)


def register(base, page, pid="P01"):
    page.goto(base + "/")
    page.fill("#pid", pid)
    page.check("#consent")
    page.click("text=Start the pre-assessment")
    page.wait_for_selector("section.question")


# --- the full participant journey -------------------------------------------

def test_participant_can_finish_the_whole_training_in_a_browser(live_app, page, evidence):
    base, app = live_app
    register(base, page)
    evidence(page, "1-pre-assessment")
    assert page.locator("section.question").count() == 10

    answer_all(page, answer_key(app, "pre"))
    page.click("#submit")
    page.wait_for_selector("#result:not(.hidden)")
    assert "10 of 10" in page.inner_text("#result")

    page.click("text=Go to the training lesson")
    page.wait_for_selector("article.lesson")
    assert "Stop, Verify, Report" in page.inner_text("article.lesson")

    page.click("#to-post")
    page.wait_for_selector("section.question")
    answer_all(page, answer_key(app, "post"))
    page.click("#submit")
    page.wait_for_selector("#result:not(.hidden)")
    evidence(page, "2-post-score", locator=page.locator("#result"))

    page.click("text=Continue")
    page.check('input[name="ease"][value="4"]')
    page.click("text=Finish")
    page.wait_for_selector("#done:not(.hidden)")

    page.goto(base + "/admin")
    page.wait_for_selector("text=Participants who finished both tests")
    row = page.locator("tr", has_text="Participants who finished both tests")
    assert row.locator("td").nth(1).inner_text() == "1"
    evidence(page, "3-dashboard", full_page=True)


# --- errors a participant could run into ------------------------------------

def test_email_address_is_refused_on_the_consent_page(live_app, page, evidence):
    base, _ = live_app
    page.goto(base + "/")
    page.fill("#pid", "jane.doe@company.com")
    page.check("#consent")
    page.click("text=Start the pre-assessment")
    page.wait_for_selector("#message:has-text('Invalid participant ID')")
    assert page.url.rstrip("/") == base
    evidence(page, "1-refused", locator=page.locator("#consent-form"))


def test_post_assessment_is_locked_until_the_pre_assessment_is_done(live_app, page):
    base, app = live_app
    app.test_client().post("/api/participants", json={"participant_id": "P02", "consent": True})
    page.goto(base + "/test/post?pid=P02")
    page.wait_for_selector("#message:has-text('pre-assessment has to be finished first')")
    assert page.is_disabled("#submit")


# --- the two usability fixes from the Unit 6 review -------------------------

def test_progress_counter_shows_how_many_questions_are_answered(live_app, page, evidence):
    base, app = live_app
    register(base, page)
    counter = page.locator("#progress")
    assert counter.inner_text() == "0 of 10 questions answered"

    key = answer_key(app, "pre")
    answer(page, "Q1", key["Q1"], 3)
    assert counter.inner_text() == "1 of 10 questions answered"

    answer(page, "Q2", key["Q2"])            # a choice but no confidence rating yet
    assert counter.inner_text() == "1 of 10 questions answered"
    answer(page, "Q2", confidence=5)
    assert counter.inner_text() == "2 of 10 questions answered"
    evidence(page, "1-counter", locator=counter)


def test_missing_questions_are_highlighted_after_submit(live_app, page, evidence):
    base, app = live_app
    register(base, page)
    key = answer_key(app, "pre")
    answer_all(page, key, skip=("Q3", "Q7"))
    answer(page, "Q7", key["Q7"])            # Q7 has a choice but no confidence rating
    page.click("#submit")

    page.wait_for_selector("section.question.needs-answer")
    highlighted = page.locator("section.question.needs-answer")
    assert [highlighted.nth(i).get_attribute("id") for i in range(highlighted.count())] == ["Q3", "Q7"]
    assert "Q3, Q7" in page.inner_text("#message")
    evidence(page, "1-highlighted", locator=page.locator("#Q3"))

    # The highlight goes away as soon as the question is finished
    answer(page, "Q3", key["Q3"], 4)
    assert page.locator("#Q3.needs-answer").count() == 0
    assert page.locator("#Q7.needs-answer").count() == 1
