const STORAGE_KEY = "octera_history";
const MAX_ENTRIES = 20;

export function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function addHistoryEntry(entry) {
  const history = [entry, ...loadHistory()].slice(0, MAX_ENTRIES);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch {
    // localStorage недоступен (приватный режим и т.п.) — молча пропускаем
  }
  return history;
}
