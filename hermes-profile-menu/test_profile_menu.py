from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).parent
AGENT = Path.home() / ".hermes" / "hermes-agent"
sys.path.insert(0, str(AGENT))

spec = importlib.util.spec_from_file_location("hermes_profile_menu", ROOT / "__init__.py")
menu = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(menu)


class ProfileMenuTests(unittest.TestCase):
    def test_registers_every_alias(self):
        seen = {}

        class Ctx:
            def register_command(self, name, handler, description="", args_hint=""):
                seen[name] = (handler, description)

        menu.register(Ctx())
        self.assertEqual(set(seen), set(menu.PROFILE_COMMANDS) | {"profiles"})
        self.assertEqual(len(seen), 12)

    def test_switch_updates_live_runner_and_active_config(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw) / ".hermes"
            (home / "profiles" / "sherlock").mkdir(parents=True)
            (home / "config.yaml").write_text(
                "gateway:\n  multiplex_profiles: true\n", encoding="utf-8"
            )

            from gateway import run as gateway_run

            config = SimpleNamespace(multiplex_profiles=True, profile_routes=[])
            runner = SimpleNamespace(config=config)
            with (
                patch.dict(
                    os.environ,
                    {
                        "HERMES_HOME": str(home),
                        "HERMES_SESSION_PLATFORM": "telegram",
                        "HERMES_SESSION_CHAT_ID": "176203333",
                    },
                    clear=False,
                ),
                patch.object(gateway_run, "_gateway_runner_ref", lambda: runner),
            ):
                result = menu._set_chat_profile("sherlock", "🔍 Шерлок")

            self.assertIn("Переключено", result)
            self.assertEqual(len(config.profile_routes), 1)
            route = config.profile_routes[0]
            self.assertEqual(route.platform, "telegram")
            self.assertEqual(route.chat_id, "176203333")
            self.assertEqual(route.profile, "sherlock")

            text = (home / "config.yaml").read_text(encoding="utf-8")
            self.assertIn("multiplex_profiles: true", text)
            self.assertIn("profile: sherlock", text)
            self.assertIn("176203333", text)

    def test_switch_replaces_only_current_chat_route(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw) / ".hermes"
            for name in ("sherlock", "femida"):
                (home / "profiles" / name).mkdir(parents=True, exist_ok=True)
            (home / "config.yaml").write_text("{}\n", encoding="utf-8")

            from gateway import run as gateway_run
            from gateway.profile_routing import parse_profile_routes

            initial = [
                {
                    "name": "mine",
                    "platform": "telegram",
                    "chat_id": "176203333",
                    "profile": "sherlock",
                },
                {
                    "name": "other",
                    "platform": "telegram",
                    "chat_id": "999",
                    "profile": "femida",
                },
            ]
            config = SimpleNamespace(
                multiplex_profiles=True,
                profile_routes=parse_profile_routes(initial),
            )
            runner = SimpleNamespace(config=config)
            with (
                patch.dict(
                    os.environ,
                    {
                        "HERMES_HOME": str(home),
                        "HERMES_SESSION_PLATFORM": "telegram",
                        "HERMES_SESSION_CHAT_ID": "176203333",
                    },
                    clear=False,
                ),
                patch.object(gateway_run, "_gateway_runner_ref", lambda: runner),
            ):
                menu._set_chat_profile("femida", "⚖️ Фемида")

            rows = menu._route_dicts(config)
            self.assertEqual(len(rows), 2)
            by_chat = {row["chat_id"]: row["profile"] for row in rows}
            self.assertEqual(by_chat, {"176203333": "femida", "999": "femida"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
