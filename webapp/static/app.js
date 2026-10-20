// Front end for the training app. Every page talks to the backend only through
// the JSON API (/api/...). Nothing is saved in the browser except the
// participant ID for the current visit.

async function callApi(method, url, body) {
  const options = { method: method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) options.body = JSON.stringify(body);
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function currentParticipant() {
  const fromUrl = new URLSearchParams(window.location.search).get("pid");
  if (fromUrl) sessionStorage.setItem("pid", fromUrl);
  return sessionStorage.getItem("pid");
}

function showMessage(text) {
  document.getElementById("message").textContent = text;
}

// Consent page: register the participant ID, then start the pre-assessment
function initConsent() {
  document.getElementById("consent-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await callApi("POST", "/api/participants", {
        participant_id: document.getElementById("pid").value,
        consent: document.getElementById("consent").checked,
      });
      sessionStorage.setItem("pid", data.participant_id);
      window.location.href = "/test/pre";
    } catch (err) {
      showMessage(err.message);
    }
  });
}

function questionHtml(q) {
  const figure = q.image
    ? `<figure><img src="${q.image}" alt="Screenshot for question ${q.number}"
         onerror="this.replaceWith(Object.assign(document.createElement('p'),{className:'missing',textContent:'Screenshot not found in the screenshots folder.'}))">
       <figcaption>${q.caption || ""}</figcaption></figure>`
    : "";
  const choices = Object.entries(q.options).map(([letter, text]) =>
    `<label class="option"><input type="radio" name="${q.item_id}" value="${letter}"> ${letter}) ${text}</label>`).join("");
  const sure = [1, 2, 3, 4, 5].map((n) =>
    `<label><input type="radio" name="${q.item_id}-conf" value="${n}"> ${n}</label>`).join("");
  return `<section class="question card" id="${q.item_id}">
      <h2>Question ${q.number}</h2>${figure}
      <p>${q.prompt}</p>${choices}
      <div class="sure">How sure are you? <span class="hint">1 = guessing, 5 = completely sure</span> ${sure}</div>
    </section>`;
}

// Pre and post assessment pages: load the questions, start the attempt, submit the answers
async function initTest(test) {
  const pid = currentParticipant();
  if (!pid) { window.location.href = "/"; return; }
  document.getElementById("who").textContent = "Participant: " + pid;
  try {
    await callApi("POST", `/api/tests/${test}/start`, { participant_id: pid });
    const questions = await callApi("GET", `/api/tests/${test}/questions`);
    document.getElementById("questions").innerHTML = questions.map(questionHtml).join("");
  } catch (err) {
    document.getElementById("questions").textContent = "";
    showMessage(err.message);
    document.getElementById("submit").disabled = true;
    return;
  }

  // When Submit is clicked, get the answer and the rating for each question
  document.getElementById("test-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const answers = {};
    document.querySelectorAll("section.question").forEach((section) => {
      const choice = section.querySelector(`input[name="${section.id}"]:checked`);
      const conf = section.querySelector(`input[name="${section.id}-conf"]:checked`);
      answers[section.id] = { choice: choice ? choice.value : null, confidence: conf ? Number(conf.value) : null };
    });

    // Send the answers to the API and show the score
    try {
      const result = await callApi("POST", `/api/tests/${test}/submit`, { participant_id: pid, answers: answers });
      document.getElementById("test-form").classList.add("hidden");
      const next = test === "pre" ? ["/training", "Go to the training lesson"] : ["/feedback", "Continue"];
      const box = document.getElementById("result");
      box.innerHTML = `<h2>Submitted</h2><p>You answered ${result.correct} of ${result.total} correctly (${result.score}%).</p>
        <a class="button" href="${next[0]}">${next[1]}</a>`;
      box.classList.remove("hidden");
      window.scrollTo(0, 0);
    } catch (err) {
      // Show the error from the API, for example a missing question
      showMessage(err.message);
    }
  });
}

function initTraining() {
  document.getElementById("to-post").addEventListener("click", () => { window.location.href = "/test/post"; });
}

function initFeedback() {
  const pid = currentParticipant();
  document.getElementById("feedback-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const ease = document.querySelector('input[name="ease"]:checked');
    try {
      await callApi("POST", "/api/feedback", {
        participant_id: pid,
        ease_rating: ease ? Number(ease.value) : null,
        comment: document.getElementById("comment").value,
      });
      document.getElementById("feedback-form").classList.add("hidden");
      document.getElementById("done").classList.remove("hidden");
    } catch (err) {
      showMessage(err.message);
    }
  });
}

function pct(value) { return value === null || value === undefined ? "n/a" : value + "%"; }

// Route names contain <test>, which the browser would read as an HTML tag
function escapeHtml(text) {
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Researcher dashboard: reads the scoring results and response times from the API
async function initAdmin() {
  const box = document.getElementById("dashboard");
  try {
    const s = await callApi("GET", "/api/results/summary");
    const perf = await callApi("GET", "/api/metrics/performance");
    const ind = Object.keys(s.per_indicator_accuracy.post).map((k) =>
      `<tr><td>${k.replace(/_/g, " ")}</td><td>${pct(s.per_indicator_accuracy.pre[k])}</td><td>${pct(s.per_indicator_accuracy.post[k])}</td></tr>`).join("");
    const people = Object.entries(s.participant_improvement).map(([pid, r]) =>
      `<tr><td>${pid}</td><td>${pct(r.pre)}</td><td>${pct(r.post)}</td><td>${r.change > 0 ? "+" : ""}${r.change} pp</td></tr>`).join("");
    const times = perf.map((r) =>
      `<tr><td>${escapeHtml(r.route)}</td><td>${r.requests}</td><td>${r.average_ms} ms</td><td>${r.p95_ms} ms</td></tr>`).join("");
    const incomplete = s.incomplete_attempts.map((a) => `${a.participant_id} (${a.test})`).join(", ") || "none";
    const met = (ok) => ok ? '<span class="ok">Met</span>' : '<span class="no">Not met</span>';
    const leftOut = s.excluded_unmatched.length ? s.excluded_unmatched.join(", ") : "none";
    box.innerHTML = `
      <h2>Success criteria</h2>
      <table><tr><th>Goal</th><th>Result</th></tr>
        <tr><td>Average score improves by at least 20 percentage points</td><td>${met(s.success_criteria.goal_3_score_improvement_20pp)}</td></tr>
        <tr><td>At least 80% of participants score 80% or higher after training</td><td>${met(s.success_criteria.goal_4_mastery_80pct_at_80)}</td></tr>
        <tr><td>Correct response rate improves by at least 20 percentage points</td><td>${met(s.success_criteria.response_rate_improvement_20pp)}</td></tr></table>
      <h2>Other measures</h2>
      <table><tr><th>Measure</th><th>Pre</th><th>Post</th></tr>
        <tr><td>Correct response rate (Q4, Q5, Q9, Q10)</td><td>${pct(s.correct_response_rate.pre)}</td><td>${pct(s.correct_response_rate.post)}</td></tr>
        <tr><td>False alarm rate (Q7, Q8)</td><td>${pct(s.false_alarm_rate.pre)}</td><td>${pct(s.false_alarm_rate.post)}</td></tr>
        <tr><td>Average confidence (1 to 5)</td><td>${s.confidence.pre ?? "n/a"}</td><td>${s.confidence.post ?? "n/a"}</td></tr></table>
      <h2>Accuracy by warning sign</h2>
      <table><tr><th>Warning sign</th><th>Pre</th><th>Post</th></tr>${ind}</table>
      <h2>Each participant</h2>
      <table><tr><th>ID</th><th>Pre</th><th>Post</th><th>Change</th></tr>${people}</table>
      <h2>API response times</h2>
      <table><tr><th>Route</th><th>Requests</th><th>Average</th><th>95th percentile</th></tr>${times}</table>
      <h2>Summary</h2>
      <table><tr><th>Measure</th><th>Result</th></tr>
        <tr><td>Participants who finished both tests</td><td>${s.participants}</td></tr>
        <tr><td>Average score before training</td><td>${pct(s.average_score.pre)}</td></tr>
        <tr><td>Average score after training</td><td>${pct(s.average_score.post)}</td></tr>
        <tr><td>Improvement</td><td>${s.average_score.improvement > 0 ? "+" : ""}${s.average_score.improvement} percentage points</td></tr>
        <tr><td>Scored 80% or higher after training</td><td>${pct(s.mastery_rate_post)}</td></tr>
        <tr><td>Left out of the results (did not finish both tests)</td><td>${leftOut}</td></tr>
        <tr><td>Unfinished tests</td><td>${incomplete}</td></tr>
        <tr><td>Feedback responses</td><td>${s.usability.responses}</td></tr>
        <tr><td>Average ease rating (1 to 5)</td><td>${s.usability.average_ease_rating ?? "n/a"}</td></tr></table>`;
  } catch (err) {
    box.textContent = err.message;
  }
}
