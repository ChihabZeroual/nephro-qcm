/** Inline SVG icons (24px, stroke, modern) */
const NS = "http://www.w3.org/2000/svg";

export function icon(name, className = "ico") {
  const paths = ICON_PATHS[name] || ICON_PATHS.home;
  return `<svg class="${className}" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;
}

const ICON_PATHS = {
  logo: `<path d="M12 4v4M12 16v4M6 12H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h2"/><path d="M18 12h2a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/><path d="M8 12h8"/><circle cx="12" cy="12" r="2"/>`,
  menu: `<path d="M4 7h16M4 12h16M4 17h16"/>`,
  home: `<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>`,
  train: `<path d="M22 12h-2l-3-9H7L4 12H2"/><path d="M5 12v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5"/><circle cx="7.5" cy="17.5" r="1.5"/><circle cx="16.5" cy="17.5" r="1.5"/>`,
  exam: `<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 12h6M9 16h4"/>`,
  lacunes: `<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>`,
  forget: `<path d="M12 2a7 7 0 0 1 7 7c0 2.5-1.2 4.7-3 6.1V18a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.9C6.2 13.7 5 11.5 5 9a7 7 0 0 1 7-7z"/><path d="M10 22h4"/>`,
  errors: `<circle cx="12" cy="12" r="9"/><path d="M15 9 9 15M9 9l6 6"/>`,
  favorites: `<path d="M12 2l3.1 6.3L22 9.3l-5 4.9 1.2 6.9L12 17.8 5.8 21.1 7 14.2 2 9.3l6.9-1z"/>`,
  search: `<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>`,
  history: `<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>`,
  courses: `<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H17l4 4v11.5A2.5 2.5 0 0 1 18.5 20H6.5A2.5 2.5 0 0 1 4 17.5z"/>`,
  reset: `<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 3v6h6"/>`,
  check: `<path d="M20 6 9 17l-5-5"/>`,
  x: `<path d="M18 6 6 18M6 6l12 12"/>`,
  brain: `<path d="M8 4c-2 0-3 1.5-3 3.5S5 11 7 11c0 2-1 3-3 4.5S4 20 8 20s4-1.5 4-3"/><path d="M16 4c2 0 3 1.5 3 3.5S19 11 17 11c0 2 1 3 3 4.5S20 20 16 20s-4-1.5-4-3"/><path d="M9 12h6"/>`,
  star: `<path d="M12 2l3.1 6.3L22 9.3l-5 4.9 1.2 6.9L12 17.8 5.8 21.1 7 14.2 2 9.3l6.9-1z"/>`,
  starOutline: `<path d="M12 2l3.1 6.3L22 9.3l-5 4.9 1.2 6.9L12 17.8 5.8 21.1 7 14.2 2 9.3l6.9-1z" fill="none"/>`,
  target: `<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>`,
  book: `<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H17l4 4v11.5A2.5 2.5 0 0 1 18.5 20H6.5A2.5 2.5 0 0 1 4 17.5z"/>`,
  warn: `<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.6 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0z"/>`,
};

export function decorateNavIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    const n = el.getAttribute("data-icon");
    const cls = el.classList.contains("ico-lg") ? "ico ico-lg" : "ico";
    el.innerHTML = icon(n, cls);
  });
}
