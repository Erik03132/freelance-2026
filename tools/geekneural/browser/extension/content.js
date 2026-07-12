// GeekNeural content script — дедупликация повторно вставляемого контекста
// в поле ввода ChatGPT / Claude / Gemini. При повторной вставке того же
// большого куска заменяет его короткой ссылкой-заглушкой и показывает бейдж
// с экономией токенов. Не трогает wire-API (безопасно для сессии).

const MIN = 256;

function findComposer() {
  // Универсальные селекторы полей ввода веб-чатов.
  return (
    document.querySelector("div[contenteditable='true']") ||
    document.querySelector("textarea") ||
    null
  );
}

function askDedup(text, force) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      { type: "gn_check", text, force },
      (res) => resolve(res || { deduped: false })
    );
  });
}

async function onPaste(e) {
  const text = (e.clipboardData || window.clipboardData).getData("text");
  if (!text || text.length < MIN) return;
  const res = await askDedup(text, false);
  if (res.deduped) {
    e.preventDefault();
    const box = findComposer();
    if (box) {
      // Вставляем только короткую ссылку вместо дублирующегося куска.
      const ref = `[↺ GeekNeural: дубликат ${res.ref} уже в контексте — повторная передача пропущена]`;
      insertText(box, ref);
      bumpBadge();
    }
  }
}

function insertText(box, text) {
  if (box.tagName === "TEXTAREA" || box.tagName === "INPUT") {
    const s = box.selectionStart, e = box.selectionEnd;
    box.value = box.value.slice(0, s) + text + box.value.slice(e);
    box.dispatchEvent(new Event("input", { bubbles: true }));
  } else {
    box.focus();
    const sel = window.getSelection();
    if (sel && sel.rangeCount) {
      const r = sel.getRangeAt(0);
      r.deleteContents();
      r.insertNode(document.createTextNode(text));
      box.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }
}

let badge = null;
function bumpBadge() {
  if (!badge) {
    badge = document.createElement("div");
    badge.style.cssText =
      "position:fixed;bottom:12px;right:12px;z-index:999999;background:#16a34a;" +
      "color:#fff;padding:4px 10px;border-radius:8px;font:12px sans-serif;opacity:.92";
    document.body.appendChild(badge);
  }
  chrome.runtime.sendMessage({ type: "gn_stats" }, (s) => {
    if (s) badge.textContent = `GeekNeural ↺ −${s.pct_saved}% (≈${s.est_tokens_saved} tok)`;
  });
}

document.addEventListener("paste", onPaste, true);
