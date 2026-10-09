import {
  loadState,
  saveState,
  recordAnswer,
  pushSession,
  toggleFavorite,
  getWeakNotions,
  aggregateDashboard,
  masteryLabel,
  getQuestionStat,
  resetAllProgress,
} from "./storage.js";
import { pickQuestions, searchQuestions, groupByTopic, compareAnswers } from "./engine.js";
import { icon, decorateNavIcons } from "./icons.js";

const main = document.getElementById("main");
const drawer = document.getElementById("drawer");
const toastEl = document.getElementById("toast");

let state = loadState();
let questions = [];
let session = null;

function toast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add("show");
  setTimeout(() => toastEl.classList.remove("show"), 2200);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function loadQuestions() {
  const res = await fetch("./data/questions.json");
  if (!res.ok) throw new Error("Impossible de charger questions.json");
  questions = await res.json();
}

function setView(view, params = {}) {
  const desktop = window.matchMedia("(min-width:720px)").matches;
  drawer.hidden = desktop ? false : true;
  setActiveNav(view);
  if (view === "home") renderHome();
  else if (view === "train") startSession({ mode: "train", ...params });
  else if (view === "exam") startSession({ mode: "exam", count: params.count || 40 });
  else if (view === "lacunes") startSession({ mode: "lacunes", pickMode: "lacunes" });
  else if (view === "forget") startSession({ mode: "forget", pickMode: "forget" });
  else if (view === "errors") renderErrors();
  else if (view === "favorites") renderFavorites();
  else if (view === "search") renderSearch();
  else if (view === "history") renderHistory();
  else if (view === "courses") renderCourses();
}

function confirmReset() {
  const ok = window.confirm(
    "Réinitialiser toute la progression ?\n\nHistorique, lacunes, favoris et statistiques seront effacés."
  );
  if (!ok) return;
  state = resetAllProgress();
  session = null;
  toast("Progression réinitialisée");
  setView("home");
}

function setActiveNav(view) {
  document.querySelectorAll(".bottom-nav-item[data-view], .drawer button[data-view]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });
}

function renderHome() {
  const d = aggregateDashboard(state, questions);
  const weak = getWeakNotions(state, 5);
  main.innerHTML = `
    <div class="card">
      <h1 class="h-with-icon">${icon("home", "ico-inline")} Tableau de bord</h1>
      <p class="muted">Coach adaptatif — examen de spécialité néphrologie</p>
      <div class="grid2" style="margin-top:12px">
        <div class="stat"><div class="num">${d.totalAnswered}</div><div class="lbl">QCM réalisés</div></div>
        <div class="stat"><div class="num">${d.successRate}%</div><div class="lbl">Taux de réussite</div></div>
        <div class="stat"><div class="num">${d.mastered}</div><div class="lbl">Notions maîtrisées</div></div>
        <div class="stat"><div class="num">${d.weak}</div><div class="lbl">Notions faibles</div></div>
      </div>
    </div>
    <div class="card">
      <h2 class="h-with-icon">${icon("target", "ico-inline")} Objectif du jour</h2>
      <p><strong>Aujourd'hui : ${d.dailyGoal} QCM</strong></p>
      <p class="muted">${weak.length || 0} lacunes · ${d.todayReview} à revoir · ${d.mastered} maîtrisées</p>
      <div class="actions actions-stack-mobile">
        <button class="btn primary" data-go="train">Entraînement (20 QCM)</button>
        <button class="btn secondary" data-go="lacunes">Mes lacunes</button>
        <button class="btn secondary" data-go="exam">Examen</button>
      </div>
    </div>
    ${
      weak.length
        ? `<div class="card"><h3 class="h-with-icon">${icon("warn", "ico-inline")} Erreurs récurrentes</h3><ul class="clean-list">${weak
            .map(
              (w) =>
                `<li><span class="level-${w.level}">${masteryLabel(w.level)}</span> ${escapeHtml(w.notion)} — ${w.errors} erreur(s)</li>`
            )
            .join("")}</ul></div>`
        : ""
    }
    <div class="card">
      <h3 class="h-with-icon">${icon("book", "ico-inline")} Banque</h3>
      <p class="muted">${questions.length} questions DEMS — strictement issues des cours extractibles (voir limitation PDF).</p>
      ${questions.length < 150 ? `<p class="muted"><strong>7 cours</strong> en attente : export texte des PDF (images). Détails : <code>COURSES_PDF_LIMITATION.md</code></p>` : ""}
    </div>
    <div class="card card-danger">
      <h3 class="h-with-icon">${icon("reset", "ico-inline")} Reset</h3>
      <p class="muted">Efface l'historique et les statistiques sur cet appareil.</p>
      <button type="button" class="btn btn-danger block" id="btnResetHome">Réinitialiser la progression</button>
    </div>
  `;
  main.querySelectorAll("[data-go]").forEach((btn) => {
    btn.addEventListener("click", () => setView(btn.dataset.go));
  });
  document.getElementById("btnResetHome").addEventListener("click", confirmReset);
}

function startSession(opts) {
  const count = opts.count || 20;
  const list = pickQuestions(questions, {
    count,
    mode: opts.pickMode || "adaptive",
    state,
    topics: opts.topics,
    notions: opts.notions,
    ids: opts.ids,
    seed: Date.now(),
  });
  if (!list.length) {
    main.innerHTML = `<div class="card"><p>Aucune question disponible pour ce mode.</p><button class="btn secondary" id="backHome">Retour</button></div>`;
    document.getElementById("backHome").onclick = () => setView("home");
    return;
  }
  session = {
    mode: opts.mode || "train",
    questions: list,
    index: 0,
    answers: [],
    startedAt: Date.now(),
    timerSec: opts.mode === "exam" ? 0 : null,
    timerId: null,
    questionStartedAt: Date.now(),
    showCorrection: false,
    selected: new Set(),
  };
  document.body.classList.add("in-session");
  if (session.mode === "exam") {
    session.timerId = setInterval(() => {
      session.timerSec += 1;
      const t = document.getElementById("examTimer");
      if (t) t.textContent = formatTime(session.timerSec);
    }, 1000);
  }
  renderQuestion();
}

function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function renderQuestion() {
  const s = session;
  const q = s.questions[s.index];
  const isExam = s.mode === "exam";
  const fav = state.favorites.includes(q.id);
  const qStat = getQuestionStat(state, q.id);

  main.innerHTML = `
    <div class="card qcm-card">
      <div class="qcm-header">
        <span>QCM ${s.index + 1} / ${s.questions.length}</span>
        ${isExam ? `<span class="timer" id="examTimer">${formatTime(s.timerSec || 0)}</span>` : ""}
        <button class="btn ghost icon-btn" id="btnFav" title="Favoris">${fav ? icon("star") : icon("starOutline")}</button>
      </div>
      <div class="qcm-topic">${icon("brain", "ico-inline")} ${escapeHtml(q.topic)} · ${escapeHtml(q.notion)}</div>
      <div class="chip-row">${(q.tags || []).slice(0, 4).map((t) => `<span class="chip">${escapeHtml(t)}</span>`).join("")}</div>
      <div class="q-text">${escapeHtml(q.question)}</div>
      <div class="options" id="options"></div>
      ${
        !s.showCorrection
          ? `<div class="qcm-actions"><button class="btn primary block" id="btnValidate" disabled>VALIDER</button></div>`
          : `<div id="correction"></div>`
      }
    </div>
  `;

  document.getElementById("btnFav").onclick = () => {
    toggleFavorite(state, q.id);
    renderQuestion();
  };

  const optWrap = document.getElementById("options");
  for (const letter of ["A", "B", "C", "D", "E"]) {
    const label = document.createElement("label");
    label.className = "opt" + (s.selected.has(letter) ? " selected" : "");
    label.innerHTML = `<input type="checkbox" value="${letter}" ${s.selected.has(letter) ? "checked" : ""} ${s.showCorrection ? "disabled" : ""} /> <div><strong>${letter}.</strong> ${escapeHtml(q.options[letter])}</div>`;
    if (!s.showCorrection) {
      label.querySelector("input").addEventListener("change", (e) => {
        if (e.target.checked) s.selected.add(letter);
        else s.selected.delete(letter);
        label.classList.toggle("selected", s.selected.has(letter));
        document.getElementById("btnValidate").disabled = s.selected.size === 0;
      });
    }
    optWrap.appendChild(label);
  }

  if (s.showCorrection) {
    renderCorrection(q);
  } else {
    document.getElementById("btnValidate").onclick = () => validateCurrent();
  }
}

function validateCurrent() {
  const s = session;
  const q = s.questions[s.index];
  const selected = [...s.selected].sort();
  const timeMs = Date.now() - s.questionStartedAt;
  const result = recordAnswer(state, q, selected, timeMs);
  saveState(state);

  s.answers.push({
    id: q.id,
    selected,
    correct: q.correctAnswers,
    ok: result.isFullyCorrect,
    optionAnalysis: result.optionAnalysis,
    timeMs,
  });

  if (s.mode === "exam") {
    s.selected = new Set();
    s.questionStartedAt = Date.now();
    if (s.index + 1 >= s.questions.length) finishExam();
    else {
      s.index += 1;
      renderQuestion();
    }
    return;
  }

  s.showCorrection = true;
  renderQuestion();
}

function renderCorrection(q) {
  const s = session;
  const last = s.answers[s.answers.length - 1];
  const cmp = compareAnswers(last.selected, q.correctAnswers);
  const labels = document.querySelectorAll(".opt");
  const letters = ["A", "B", "C", "D", "E"];
  letters.forEach((letter, i) => {
    const el = labels[i];
    if (q.correctAnswers.includes(letter) && last.selected.includes(letter)) el.classList.add("correct");
    else if (q.correctAnswers.includes(letter) && !last.selected.includes(letter)) el.classList.add("missed");
    else if (!q.correctAnswers.includes(letter) && last.selected.includes(letter)) el.classList.add("wrong");
  });

  const nStat = state.notionStats[q.notion];
  const qStat = getQuestionStat(state, q.id);
  const warnRecurrent = qStat.errors >= 2 ? `<div class="warn-box">⚠️ Tu as déjà fait cette erreur ${qStat.errors} fois sur cette question / notion.</div>` : "";

  const explain = letters
    .map((L) => {
      const ok = q.correctAnswers.includes(L);
      return `<div class="explain-item">${ok ? "✅" : "❌"} <strong>${L}.</strong> ${escapeHtml(q.explanation[L] || "")}</div>`;
    })
    .join("");

  const micro =
    !last.ok && nStat?.errors >= 2
      ? `<div class="mini-rev">🧠 MINI-RÉVISION<br>${escapeHtml(q.keyPoint)}</div>`
      : "";

  const analysis =
    cmp.missed.length || cmp.falsePicks.length
      ? `<p class="muted">Analyse : ${cmp.hits.length ? `acquis (${cmp.hits.join(", ")})` : ""}${
          cmp.falsePicks.length ? ` · choix erronés (${cmp.falsePicks.join(", ")})` : ""
        }${cmp.missed.length ? ` · oublis (${cmp.missed.join(", ")})` : ""}</p>`
      : "";

  document.getElementById("correction").innerHTML = `
    <div class="correction">
      <h3>${last.ok ? "✅ Bonne réponse" : "❌ Correction"}</h3>
      <p>Bonnes réponses : <strong>${q.correctAnswers.join(" + ")}</strong></p>
      ${analysis}
      <h4>🧠 Explication</h4>
      ${explain}
      <div class="key-point">📌 À retenir<br><strong>${escapeHtml(q.keyPoint)}</strong></div>
      ${q.sourceRef ? `<p class="muted source-ref">📎 ${escapeHtml(q.sourceRef)}</p>` : ""}
      ${warnRecurrent}
      ${micro}
      <div class="actions">
        <button class="btn primary block" id="btnNext">QUESTION SUIVANTE →</button>
      </div>
    </div>
  `;
  document.getElementById("btnNext").onclick = () => {
    s.showCorrection = false;
    s.selected = new Set();
    s.questionStartedAt = Date.now();
    if (s.index + 1 >= s.questions.length) finishTraining();
    else {
      s.index += 1;
      renderQuestion();
    }
  };
}

function finishTraining() {
  const s = session;
  const ok = s.answers.filter((a) => a.ok).length;
  const score = Math.round((100 * ok) / s.answers.length);
  pushSession(state, {
    date: new Date().toISOString(),
    mode: s.mode,
    count: s.answers.length,
    score,
    durationMs: Date.now() - s.startedAt,
    errors: s.answers.filter((a) => !a.ok).map((a) => a.id),
  });
  session = null;
  document.body.classList.remove("in-session");
  main.innerHTML = `
    <div class="card">
      <h2>Session terminée</h2>
      <p><strong>${score}%</strong> — ${ok}/${s.answers.length} correctes</p>
      <p class="muted">Profil mis à jour. Consulte 🔴 Mes lacunes pour cibler tes oublis.</p>
      <div class="actions">
        <button class="btn primary" id="again">Nouvelle session</button>
        <button class="btn secondary" id="home">Accueil</button>
      </div>
    </div>`;
  document.getElementById("again").onclick = () => setView("train");
  document.getElementById("home").onclick = () => setView("home");
}

function finishExam() {
  if (session.timerId) clearInterval(session.timerId);
  const s = session;
  const ok = s.answers.filter((a) => a.ok).length;
  const score = Math.round((100 * ok) / s.answers.length);
  pushSession(state, {
    date: new Date().toISOString(),
    mode: "exam",
    count: s.answers.length,
    score,
    durationMs: Date.now() - s.startedAt,
    errors: s.answers.filter((a) => !a.ok).map((a) => a.id),
  });

  const wrongItems = s.answers
    .filter((a) => !a.ok)
    .map((a) => {
      const q = s.questions.find((x) => x.id === a.id);
      return `<li>${escapeHtml(q?.notion || a.id)} — attendu ${a.correct.join("+")}, reçu ${a.selected.join("+") || "—"}</li>`;
    })
    .join("");

  session = null;
  document.body.classList.remove("in-session");
  main.innerHTML = `
    <div class="card">
      <h2>📝 Correction examen</h2>
      <p>Score : <strong>${score}%</strong> · Durée ${formatTime(Math.floor((Date.now() - s.startedAt) / 1000))}</p>
      <h3>Erreurs</h3>
      <ul>${wrongItems || "<li>Aucune — excellent !</li>"}</ul>
      <div class="actions">
        <button class="btn primary" id="lac">🔴 Travailler mes lacunes</button>
        <button class="btn secondary" id="home">Accueil</button>
      </div>
    </div>`;
  document.getElementById("lac").onclick = () => setView("lacunes");
  document.getElementById("home").onclick = () => setView("home");
}

function renderErrors() {
  const ids = Object.entries(state.questionStats)
    .filter(([, st]) => st.errors > 0)
    .sort((a, b) => b[1].errors - a[1].errors)
    .map(([id]) => id);
  const items = ids
    .slice(0, 80)
    .map((id) => questions.find((q) => q.id === id))
    .filter(Boolean);
  main.innerHTML = `
    <div class="card">
      <h2>❌ Mes erreurs</h2>
      <p class="muted">${items.length} questions avec au moins une erreur</p>
      <button class="btn primary block" id="redo" ${items.length ? "" : "disabled"}>Refaire ces questions</button>
      <div style="margin-top:12px">${items
        .slice(0, 15)
        .map(
          (q) =>
            `<div class="list-item" data-id="${q.id}"><strong>${escapeHtml(q.topic)}</strong><br><span class="muted">${escapeHtml(q.notion)}</span></div>`
        )
        .join("")}</div>
    </div>`;
  document.getElementById("redo")?.addEventListener("click", () => {
    startSession({ mode: "train", notions: null, count: Math.min(30, items.length), pickMode: "mixed", ids: items.map((q) => q.id) });
  });
}

function renderFavorites() {
  const items = state.favorites.map((id) => questions.find((q) => q.id === id)).filter(Boolean);
  main.innerHTML = `
    <div class="card">
      <h2>⭐ Mes favoris</h2>
      <p class="muted">${items.length} question(s)</p>
      <button class="btn primary block" id="redoFav" ${items.length ? "" : "disabled"}>Réviser mes favoris</button>
      <div style="margin-top:12px">${items
        .map(
          (q) =>
            `<div class="list-item">${escapeHtml(q.topic)} — ${escapeHtml(q.question.slice(0, 120))}…</div>`
        )
        .join("") || "<p class='muted'>Aucun favori pour l'instant.</p>"}</div>
    </div>`;
  document.getElementById("redoFav")?.addEventListener("click", () => {
    startSession({ mode: "train", count: items.length, ids: state.favorites });
  });
}

function renderSearch() {
  main.innerHTML = `
    <div class="card">
      <h2>🔎 Recherche</h2>
      <input class="search-input" id="searchBox" placeholder="hyperkaliémie, GTTK, SIADH…" />
      <div id="searchResults"></div>
    </div>`;
  const box = document.getElementById("searchBox");
  const results = document.getElementById("searchResults");
  box.addEventListener("input", () => {
    const found = searchQuestions(questions, box.value).slice(0, 40);
    results.innerHTML = found
      .map(
        (q) =>
          `<div class="list-item" data-qid="${q.id}"><strong>${escapeHtml(q.topic)}</strong> · ${escapeHtml(q.notion)}<br>${escapeHtml(q.question.slice(0, 140))}…</div>`
      )
      .join("") || `<p class="muted">Aucun résultat</p>`;
    results.querySelectorAll("[data-qid]").forEach((el) => {
      el.addEventListener("click", () => {
        startSession({ mode: "train", count: 1, ids: [el.dataset.qid] });
      });
    });
  });
}

function renderHistory() {
  main.innerHTML = `
    <div class="card">
      <h2>📅 Historique</h2>
      ${
        state.sessions.length
          ? state.sessions
              .map((s) => {
                const d = new Date(s.date);
                const day = d.toLocaleDateString("fr-FR");
                return `<div class="list-item"><strong>${day}</strong> — ${s.count} QCM · ${s.score}% · mode ${s.mode}<br><span class="muted">${s.errors?.length || 0} erreur(s)</span></div>`;
              })
              .join("")
          : "<p class='muted'>Aucune session enregistrée.</p>"
      }
    </div>`;
}

function renderCourses() {
  const byTopic = groupByTopic(questions);
  main.innerHTML = `<div class="card"><h2>📚 Par cours</h2><p class="muted">10 cours — ${questions.length} QCM</p></div>`;
  for (const [topic, list] of byTopic) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<h3>${escapeHtml(topic)}</h3><p class="muted">${list.length} questions</p><button class="btn secondary block">Session (${Math.min(20, list.length)} QCM)</button>`;
    card.querySelector("button").addEventListener("click", () => {
      startSession({ mode: "train", topics: [topic], count: 20, pickMode: "mixed" });
    });
    main.appendChild(card);
  }
}

function wireNav() {
  document.getElementById("btnNav").addEventListener("click", () => {
    drawer.hidden = !drawer.hidden;
  });
  document.getElementById("btnNavMore")?.addEventListener("click", () => {
    drawer.hidden = !drawer.hidden;
  });
  document.getElementById("btnResetNav")?.addEventListener("click", confirmReset);
  const navClick = (btn) => {
    if (btn.dataset.view) setView(btn.dataset.view);
    if (!window.matchMedia("(min-width:720px)").matches) drawer.hidden = true;
  };
  drawer.querySelectorAll("button[data-view]").forEach((btn) => {
    btn.addEventListener("click", () => navClick(btn));
  });
  document.querySelectorAll(".bottom-nav-item[data-view]").forEach((btn) => {
    btn.addEventListener("click", () => navClick(btn));
  });
}

async function init() {
  decorateNavIcons();
  wireNav();
  try {
    await loadQuestions();
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("./sw.js").catch(() => {});
    }
    setView("home");
  } catch (e) {
    main.innerHTML = `<div class="card"><h2>Erreur</h2><p>${escapeHtml(e.message)}</p><p class="muted">Lance l'app via un serveur local (voir README) : <code>py -3 -m http.server 8080</code> dans le dossier <code>app</code>.</p></div>`;
  }
}

init();
