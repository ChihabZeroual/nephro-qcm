export function shuffle(arr, rng = Math.random) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function rngFromSeed(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

export function pickQuestions(all, {
  count = 20,
  topics = null,
  notions = null,
  ids = null,
  mode = "mixed",
  seed = Date.now(),
  state = null,
} = {}) {
  let pool = all;
  if (topics?.length) pool = pool.filter((q) => topics.includes(q.topic));
  if (notions?.length) pool = pool.filter((q) => notions.includes(q.notion));
  if (ids?.length) pool = pool.filter((q) => ids.includes(q.id));

  const rand = rngFromSeed(seed);

  if (mode === "lacunes" && state) {
    const weak = Object.entries(state.notionStats || {})
      .filter(([, s]) => s.errors >= 1 || s.level <= 2)
      .sort((a, b) => b[1].errors - a[1].errors || a[1].level - b[1].level)
      .map(([n]) => n);
    if (weak.length) {
      const weighted = [];
      for (const q of pool) {
        const idx = weak.indexOf(q.notion);
        const w = idx === -1 ? 1 : 8 - Math.min(idx, 6);
        for (let i = 0; i < w; i += 1) weighted.push(q);
      }
      pool = weighted;
    }
  }

  if (mode === "forget" && state) {
    const now = Date.now();
    pool = pool.filter((q) => {
      const ns = state.notionStats?.[q.notion];
      if (!ns) return false;
      return (
        ns.errors >= 2 ||
        (ns.nextReviewAt && ns.nextReviewAt <= now) ||
        (ns.streak < 2 && ns.attempts >= 2)
      );
    });
    if (!pool.length) pool = all.filter((q) => state.notionStats?.[q.notion]?.errors >= 1);
  }

  if (mode === "adaptive" && state) {
    const weighted = pool.map((q) => {
      const ns = state.notionStats?.[q.notion];
      let w = 1;
      if (!ns) w = 2;
      else {
        w += ns.errors * 2;
        if (ns.level <= 2) w += 4;
        if (ns.nextReviewAt && ns.nextReviewAt <= Date.now()) w += 3;
        if (ns.level >= 4) w = Math.max(1, w - 2);
      }
      return { q, w };
    });
    const bag = [];
    for (const { q, w } of weighted) for (let i = 0; i < w; i += 1) bag.push(q);
    pool = bag;
  }

  const seen = new Set();
  const out = [];
  const shuffled = shuffle(pool, rand);
  for (const q of shuffled) {
    if (seen.has(q.id)) continue;
    seen.add(q.id);
    out.push(q);
    if (out.length >= count) break;
  }
  return out;
}

export function searchQuestions(all, query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return all.filter((item) => {
    const hay = [
      item.question,
      item.topic,
      item.notion,
      item.chapter,
      ...(item.tags || []),
      ...Object.values(item.options || {}),
    ]
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  });
}

export function groupByTopic(questions) {
  const map = new Map();
  for (const q of questions) {
    if (!map.has(q.topic)) map.set(q.topic, []);
    map.get(q.topic).push(q);
  }
  return map;
}

export function compareAnswers(selected, correct) {
  const s = new Set(selected);
  const c = new Set(correct);
  return {
    hits: [...c].filter((x) => s.has(x)),
    missed: [...c].filter((x) => !s.has(x)),
    falsePicks: [...s].filter((x) => !c.has(x)),
  };
}
