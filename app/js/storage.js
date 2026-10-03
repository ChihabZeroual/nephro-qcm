const STORAGE_KEY = "nephro-qcm-coach-v1";

const defaultState = () => ({
  version: 1,
  notionStats: {},
  questionStats: {},
  favorites: [],
  sessions: [],
  dailyGoal: 20,
});

export function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState();
    const parsed = JSON.parse(raw);
    return { ...defaultState(), ...parsed };
  } catch {
    return defaultState();
  }
}

export function resetAllProgress() {
  const fresh = defaultState();
  saveState(fresh);
  return fresh;
}

export function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function getNotionStat(state, notion) {
  if (!state.notionStats[notion]) {
    state.notionStats[notion] = {
      attempts: 0,
      correct: 0,
      errors: 0,
      streak: 0,
      lastErrorAt: null,
      lastSeenAt: null,
      nextReviewAt: null,
      level: 0,
    };
  }
  return state.notionStats[notion];
}

export function getQuestionStat(state, id) {
  if (!state.questionStats[id]) {
    state.questionStats[id] = {
      attempts: 0,
      correct: 0,
      errors: 0,
      lastErrorAt: null,
      lastSeenAt: null,
    };
  }
  return state.questionStats[id];
}

export function masteryLabel(level) {
  const map = [
    "🔴 inconnue",
    "🟥 très faible",
    "🟠 fragile",
    "🟡 correcte",
    "🟢 maîtrisée",
    "🔵 très bien maîtrisée",
  ];
  return map[Math.min(5, Math.max(0, level))] ?? map[0];
}

export function computeLevel(stat) {
  if (stat.attempts === 0) return 0;
  const rate = stat.correct / stat.attempts;
  if (stat.errors >= 3 && rate < 0.5) return 1;
  if (stat.errors >= 2 && rate < 0.6) return 2;
  if (rate >= 0.85 && stat.streak >= 3 && stat.attempts >= 4) return 5;
  if (rate >= 0.75 && stat.streak >= 2) return 4;
  if (rate >= 0.55) return 3;
  return 2;
}

export function recordAnswer(state, question, selected, timeMs) {
  const correctSet = new Set(question.correctAnswers);
  const selectedSet = new Set(selected);
  const isFullyCorrect =
    correctSet.size === selectedSet.size &&
    [...correctSet].every((x) => selectedSet.has(x));

  const qStat = getQuestionStat(state, question.id);
  const nStat = getNotionStat(state, question.notion);
  const now = Date.now();

  qStat.attempts += 1;
  qStat.lastSeenAt = now;
  nStat.attempts += 1;
  nStat.lastSeenAt = now;

  const optionAnalysis = {};
  for (const letter of ["A", "B", "C", "D", "E"]) {
    const should = correctSet.has(letter);
    const picked = selectedSet.has(letter);
    if (should && picked) optionAnalysis[letter] = "known";
    else if (should && !picked) optionAnalysis[letter] = "missed";
    else if (!should && picked) optionAnalysis[letter] = "false_positive";
    else optionAnalysis[letter] = "ok_ignored";
  }

  let intervalHours = 24;
  if (isFullyCorrect) {
    qStat.correct += 1;
    nStat.correct += 1;
    nStat.streak += 1;
    intervalHours = Math.min(720, 6 * nStat.streak ** 2);
  } else {
    qStat.errors += 1;
    nStat.errors += 1;
    nStat.streak = 0;
    nStat.lastErrorAt = now;
    qStat.lastErrorAt = now;
    intervalHours = nStat.errors >= 3 ? 1 : nStat.errors >= 2 ? 2 : 4;
  }

  nStat.level = computeLevel(nStat);
  nStat.nextReviewAt = now + intervalHours * 3600 * 1000;

  return {
    isFullyCorrect,
    optionAnalysis,
    timeMs,
    nStat: { ...nStat },
  };
}

export function pushSession(state, session) {
  state.sessions.unshift(session);
  state.sessions = state.sessions.slice(0, 60);
  saveState(state);
}

export function toggleFavorite(state, id) {
  const i = state.favorites.indexOf(id);
  if (i >= 0) state.favorites.splice(i, 1);
  else state.favorites.push(id);
  saveState(state);
}

export function getWeakNotions(state, limit = 12) {
  return Object.entries(state.notionStats)
    .map(([notion, s]) => ({
      notion,
      ...s,
      priority: s.errors * 3 + (s.level <= 2 ? 5 : 0) + (s.lastErrorAt ? 2 : 0),
    }))
    .filter((x) => x.attempts > 0 && (x.errors >= 1 || x.level <= 2))
    .sort((a, b) => b.priority - a.priority || b.errors - a.errors)
    .slice(0, limit);
}

export function getTodayReviewNotions(state) {
  const now = Date.now();
  return Object.entries(state.notionStats)
    .filter(([, s]) => s.nextReviewAt && s.nextReviewAt <= now)
    .map(([notion, s]) => ({ notion, ...s }));
}

export function aggregateDashboard(state, questions) {
  const totalAnswered = Object.values(state.questionStats).reduce(
    (a, s) => a + s.attempts,
    0
  );
  const correct = Object.values(state.questionStats).reduce(
    (a, s) => a + s.correct,
    0
  );
  const notions = Object.values(state.notionStats);
  const mastered = notions.filter((n) => n.level >= 4).length;
  const weak = notions.filter((n) => n.level <= 2 && n.attempts > 0).length;
  const recurrent = getWeakNotions(state, 8);
  const todayReview = getTodayReviewNotions(state).length;
  return {
    totalQuestions: questions.length,
    totalAnswered,
    successRate: totalAnswered ? Math.round((100 * correct) / totalAnswered) : 0,
    mastered,
    weak,
    todayReview,
    recurrent,
    dailyGoal: state.dailyGoal,
  };
}
