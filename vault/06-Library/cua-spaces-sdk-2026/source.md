---
type: article-digest
tags: [cua, computer-use, source]
status: done
updated: 2026-10-25
---

# Source: Cua Spaces SDK (верификация 25-26.10.2026)

## Первоисточники

1. **Cua Spaces docs**
   https://cua.ai/docs/spaces
   Цитата: «A **Space** is one desktop on one of those computers, set up for a task. Your agent runs commands in it and uses its apps and browser. You see the same screen and take over when you want»
   Цитата: «You bring the computers: a Mac on your desk, a spare Linux box, a VM in your own cloud account. Cua does not rent them»
   Цитата: «The `cua` CLI, the MCP server and the SDKs (Python, TypeScript, Swift and Rust) use the same Spaces as the app»

2. **Cua SDK — Run a coding agent in a sandbox**
   https://cua.ai/docs/cua-sdk/guides/run-a-coding-agent
   Цитата: «`sandbox.agents()` runs a coding-agent harness (Claude Code, Codex, Gemini CLI, OpenCode, Goose, ...) inside the sandbox. The SDK installs the harness from pinned, checksum-verified sources, drives it over the Agent Client Protocol (agentclientprotocol.com), and normalizes its output into events»
   Цитата: «A run lives in the sandbox (state under `~/.cua/agents/<run>`), so it keeps working after your process exits; any client can reattach later»

3. **Cua CLI reference — cua agent**
   https://cua.ai/docs/cua-cli/reference/cli/agent
   Команды: `agent run` (start in sandbox, returns at once unless --follow), `agent create` (persistent agent, memory in Cua Volume, outlives its Space), `agent ls / logs / send / interrupt`.

4. **Cua Spaces — spaces.cua.ai (лендинг, early access)**
   https://spaces.cua.ai/
   Цитата: «Each Space starts with permissions granted and tools installed, so your agent doesn't stop at a permission dialog»
   Цитата: «Free now: Spaces on every computer you connect; Teleport, multiplayer and agent-ready Spaces; The hosted relay is free during early access»
   Цитата: «Claude Code, Codex, Cursor, Gemini CLI, Cline, Kiro and OpenClaw connect through the Cua MCP server»

5. **Cua (главный сайт)**
   https://cua.ai/
   Цитата: «The open-source driver under Spaces lets an agent use native desktop apps on macOS, Windows and Linux without taking over your cursor or keyboard. MIT licensed, and you can use it without Spaces»
   Цитата: «macOS Spaces are virtual machines built locally with Lume. Linux images run too»

6. **TechCityAuthority — независимый разбор (20.10.2026)**
   https://www.techcityauthority.com/2026/10/cua-spaces-sdk-bring-your-own-computer.html
   Цитата: «Cua has released the Cua Spaces SDK, a toolkit that lets developers give an AI agent its own computer to work on»
   Цитата: «Its main GitHub project has more than 30,000 stars and uses the MIT license»
   Цитата: «Cua announced the SDK in a thread on X» (x.com/trycua/status/2112228154651881479)

7. **GitHub trycua/cua**
   https://github.com/trycua/cua
   Цитата: «Spaces run on your Mac, on other machines you own, and in your own cloud account (AWS, Google Cloud or Modal)»
   Цитата: «Your sessions stay in the Cua Keyvault, encrypted on your Mac, and reach a Space only after you approve»
   Ключевой пример: `examples/agents-in-sandboxes/tour.py` (запуск end-to-end).

## Умолчания/расхождения с дропом

- **E2B/Daytona**: дроп перечислил как песочницы-таргеты; в собранных результатах явного упоминания не видно (docs говорят «a sandbox service») — перепроверить в docs/cua-sdk/guides/local-runtimes при внедрении.
- **Hermes**: упоминался в прошлом разборе (21.10, sample cua-bots-macos); в новом Spaces-списке харнесс-структур фигурируют Claude Code, Codex, Cursor, Gemini CLI, Cline, Kiro, OpenClaw, OpenCode, Goose.
- Лицензии не изменились: driver MIT; Spaces app — FSL-1.1-MIT (см. LICENSING.md корня), для внутреннего использования ок.

## Локальное связанное

- ACTIVE_TASKS 🐨 CUA (разбор 21.10.2026 + апдейт 25.10.2026): CUA-1 запланирован после 15.11.2026 (апгрейд железа); новый блок — CLI-путь `cua agent run` как лёгкая точка входа.
- Наш стек: AGENTS.md OR-2 Worktree-per-Task; claude-handoff; OpenCode харнесс.
