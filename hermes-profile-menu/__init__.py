"""Telegram menu aliases for live Hermes multiplex profile routing.

One gateway owns the Telegram token.  These slash commands update the
``gateway.profile_routes`` entry for the current Telegram chat so the next
message runs inside the selected profile's config, SOUL, skills and memory.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

# command -> (profile id, human label)
PROFILE_COMMANDS: dict[str, tuple[str, str]] = {
    "chief": ("personal", "👑 Главный"),
    "default": ("default", "⚙️ Базовый"),
    "batrak": ("batrak", "🤖 Батрак / поиск работы"),
    "bridge": ("bridge", "🌉 Bridge"),
    "defender": ("defender", "🛡️ Защитник"),
    "english": ("english-tutor", "🇬🇧 Учитель английского"),
    "femida": ("femida", "⚖️ Фемида"),
    "financier": ("financier", "💰 Финансист"),
    "aibolit": ("health", "⚕️ Айболит"),
    "marketer": ("marketer", "📣 Маркетолог"),
    "sherlock": ("sherlock", "🔍 Шерлок"),
}


def _session_origin() -> tuple[str, str]:
    from gateway.session_context import get_session_env

    platform = get_session_env("HERMES_SESSION_PLATFORM", "").strip().lower()
    chat_id = get_session_env("HERMES_SESSION_CHAT_ID", "").strip()
    return platform, chat_id


def _runner():
    from gateway import run as gateway_run

    return gateway_run._gateway_runner_ref()


def _route_dicts(config: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for route in list(getattr(config, "profile_routes", None) or []):
        if isinstance(route, dict):
            rows.append(dict(route))
        else:
            try:
                rows.append(asdict(route))
            except Exception:
                continue
    return rows


def _persist_routes(rows: list[dict[str, Any]]) -> None:
    import os
    from pathlib import Path
    from hermes_cli.config import atomic_config_write, read_user_config_raw

    # Always persist into the process-level multiplex gateway home, never into
    # the currently routed profile's context-local HERMES_HOME override.
    process_home = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes")
    path = process_home / "config.yaml"
    cfg = read_user_config_raw(path)
    cfg["profile_routes"] = rows
    gateway = cfg.setdefault("gateway", {})
    if not isinstance(gateway, dict):
        gateway = {}
        cfg["gateway"] = gateway
    gateway["multiplex_profiles"] = True
    atomic_config_write(path, cfg)


def _set_chat_profile(profile: str, label: str) -> str:
    platform, chat_id = _session_origin()
    if platform != "telegram" or not chat_id:
        return "Эта команда переключает профиль только внутри Telegram-чата."

    runner = _runner()
    if runner is None:
        return "Gateway ещё не готов. Повтори команду через несколько секунд."
    if not getattr(runner.config, "multiplex_profiles", False):
        return "Multiplex-профили выключены. Нужен один перезапуск gateway после установки меню."

    from hermes_cli.profiles import profile_exists

    if profile != "default" and not profile_exists(profile):
        return f"Профиль '{profile}' отсутствует на VPS."

    from gateway.profile_routing import parse_profile_routes

    route_name = f"telegram-menu-{chat_id}"
    rows = [
        row
        for row in _route_dicts(runner.config)
        if not (
            str(row.get("platform") or "") == "telegram"
            and str(row.get("chat_id") or "") == chat_id
            and not row.get("thread_id")
        )
    ]
    rows.append(
        {
            "name": route_name,
            "platform": "telegram",
            "chat_id": chat_id,
            "profile": profile,
            "enabled": True,
        }
    )
    runner.config.profile_routes = parse_profile_routes(rows)
    _persist_routes(rows)
    return f"✅ Переключено: {label}\nПрофиль: `{profile}`\nСледующее сообщение пойдёт этому специалисту."


def _show_profiles(_raw_args: str = "") -> str:
    platform, chat_id = _session_origin()
    selected = "default"
    runner = _runner()
    if runner is not None and platform == "telegram" and chat_id:
        for row in _route_dicts(runner.config):
            if (
                str(row.get("platform") or "") == "telegram"
                and str(row.get("chat_id") or "") == chat_id
                and not row.get("thread_id")
                and row.get("enabled", True)
            ):
                selected = str(row.get("profile") or "default")
                break

    lines = [f"🧭 Текущий профиль: `{selected}`", "", "Выбери специалиста:"]
    for command, (profile, label) in PROFILE_COMMANDS.items():
        marker = "●" if profile == selected else "○"
        lines.append(f"{marker} /{command} — {label}")
    return "\n".join(lines)


def _make_handler(profile: str, label: str):
    def handler(_raw_args: str = "") -> str:
        return _set_chat_profile(profile, label)

    return handler


def register(ctx) -> None:
    for command, (profile, label) in PROFILE_COMMANDS.items():
        ctx.register_command(
            command,
            handler=_make_handler(profile, label),
            description=f"{label}: переключить профиль",
        )
    ctx.register_command(
        "profiles",
        handler=_show_profiles,
        description="🧭 Показать всех специалистов",
    )
