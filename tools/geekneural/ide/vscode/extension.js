// GeekNeural VS Code extension (уровень 4).
// Команда копирует содержимое активного файла в буфер обмена через ядро
// дедупликации (core/cli.py). При повторном копировании того же файла в
// сессии в буфер попадает только короткая ссылка -> экономия токенов.

const { execFileSync } = require("child_process");
const path = require("path");
const vscode = require("vscode");

function root() {
  return vscode.workspace
    .getConfiguration("geekneural")
    .get("root", path.resolve(__dirname, "..", ".."));
}

function gnRead(filePath, force) {
  const cli = path.join(root(), "core", "cli.py");
  const out = execFileSync(
    process.platform === "win32" ? "python" : "python3",
    [cli, "read", filePath, "--json"].concat(force ? ["--force"] : []),
    { encoding: "utf-8", env: { ...process.env, GEEKNEURAL_ROOT: root() } }
  );
  return JSON.parse(out);
}

async function copyToChat() {
  const ed = vscode.window.activeTextEditor;
  if (!ed) {
    vscode.window.showErrorMessage("GeekNeural: нет активного файла");
    return;
  }
  const file = ed.document.fileName;
  let res;
  try {
    res = gnRead(file, false);
  } catch (e) {
    vscode.window.showErrorMessage("GeekNeural: " + e.message);
    return;
  }
  await vscode.env.clipboard.writeText(res.content);
  if (res.deduped) {
    vscode.window.showInformationMessage(
      `GeekNeural ↺ дубликат ${res.ref} — в буфере только ссылка (токены сэкономлены)`
    );
  } else {
    vscode.window.showInformationMessage(
      `GeekNeural: файл в буфере (${res.bytes_sent} байт)${res.reason === "volatile_or_tiny" ? " — volatile/tiny, не дедуплицирован" : ""}`
    );
  }
}

function showStats() {
  const cli = path.join(root(), "core", "cli.py");
  try {
    const out = execFileSync(
      process.platform === "win32" ? "python" : "python3",
      [cli, "stats"],
      { encoding: "utf-8", env: { ...process.env, GEEKNEURAL_ROOT: root() } }
    );
    const s = JSON.parse(out);
    vscode.window.showInformationMessage(
      `GeekNeural: чтений ${s.reads}, дедуп ${s.deduped}, экономия ${s.pct_saved}% (≈${s.est_tokens_saved} токенов)`
    );
  } catch (e) {
    vscode.window.showErrorMessage("GeekNeural: " + e.message);
  }
}

function clearSession() {
  const cli = path.join(root(), "core", "cli.py");
  try {
    execFileSync(
      process.platform === "win32" ? "python" : "python3",
      [cli, "clear"],
      { encoding: "utf-8", env: { ...process.env, GEEKNEURAL_ROOT: root() } }
    );
    vscode.window.showInformationMessage("GeekNeural: сессия сброшена");
  } catch (e) {
    vscode.window.showErrorMessage("GeekNeural: " + e.message);
  }
}

function activate(ctx) {
  ctx.subscriptions.push(
    vscode.commands.registerCommand("geekneural.readToChat", copyToChat),
    vscode.commands.registerCommand("geekneural.stats", showStats),
    vscode.commands.registerCommand("geekneural.clear", clearSession)
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
