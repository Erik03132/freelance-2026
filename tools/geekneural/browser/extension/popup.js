function render() {
  chrome.runtime.sendMessage({ type: "gn_stats" }, (s) => {
    const el = document.getElementById("stats");
    if (!s) { el.textContent = "нет данных"; return; }
    el.innerHTML =
      `Чтений: <b>${s.reads}</b><br>` +
      `Дедуплировано: <b>${s.deduped}</b><br>` +
      `Экономия: <b>${s.pct_saved}%</b><br>` +
      `Токенов сэкономлено: <b>≈${s.est_tokens_saved}</b>`;
  });
}
document.getElementById("clear").addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "gn_clear" }, render);
});
render();
setInterval(render, 1000);
