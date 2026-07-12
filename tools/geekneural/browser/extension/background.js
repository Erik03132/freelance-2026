// GeekNeural background — session dedup cache (mirrors core/dedup.py logic).
// Без телеметрии: всё хранится локально в chrome.storage.session.

const MIN_DEDUP_CHARS = 256;

function hashText(text) {
  // djb2 + длина — быстрый контентный отпечаток для эвристики дедупа.
  let h = 5381;
  for (let i = 0; i < text.length; i++) {
    h = ((h << 5) + h + text.charCodeAt(i)) | 0;
  }
  return (h >>> 0).toString(16) + ":" + text.length;
}

const state = {
  seen: {},          // hash -> {count, bytes}
  bytesRaw: 0,
  bytesSent: 0,
  reads: 0,
  deduped: 0,
};

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === "gn_check") {
    const text = msg.text || "";
    const force = !!msg.force;
    state.reads++;
    const bytes = text.length * 2; // ~UTF-16
    state.bytesRaw += bytes;
    if (!force && text.length >= MIN_DEDUP_CHARS && state.seen[hashText(text)]) {
      state.seen[hashText(text)].count++;
      state.deduped++;
      state.bytesSent += 24; // только ссылка-заглушка
      sendResponse({ deduped: true, ref: "gn:" + hashText(text).slice(0, 16) });
    } else {
      if (text.length >= MIN_DEDUP_CHARS) {
        state.seen[hashText(text)] = state.seen[hashText(text)] || { count: 0 };
      }
      state.bytesSent += bytes;
      sendResponse({ deduped: false });
    }
    return true;
  }
  if (msg.type === "gn_stats") {
    const saved = state.bytesRaw - state.bytesSent;
    const pct = state.bytesRaw ? (100 * saved) / state.bytesRaw : 0;
    sendResponse({
      reads: state.reads,
      deduped: state.deduped,
      pct_saved: +pct.toFixed(1),
      est_tokens_saved: Math.max(0, Math.floor(saved / 4)),
    });
    return true;
  }
  if (msg.type === "gn_clear") {
    state.seen = {}; state.bytesRaw = 0; state.bytesSent = 0;
    state.reads = 0; state.deduped = 0;
    sendResponse({ ok: true });
    return true;
  }
});
