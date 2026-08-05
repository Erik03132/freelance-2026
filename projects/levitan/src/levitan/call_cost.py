"""LV-1: Счётчик себестоимости звонка для Levitan.

Фиксирует по каждому звонку: модель, версию промпта, токены вход/выход/кэш,
время до первого звука, исход, тест-флаг, хэш номера (без ПДн) и стоимость
по статьям. Данные — в SQLite (data/call_cost.sqlite3).

Обоснование (статья Habr 1066792): токены = 66% счёта звонка, кэш 80%
(иначе втрое дороже), длина промпта > длительность разговора. Счётчик —
обоснование цены клиенту вместо «кажется, полезно».

Использование:
    from call_cost import CallCost
    cc = CallCost()
    cc.record(call_id="...", phone_hash="sha256...", model="deepseek-chat",
              prompt_version="v3", tokens_in=1200, tokens_out=300, tokens_cached=1000,
              first_voice_ms=554, outcome="completed", test=True,
              cost_mango=0.5, cost_stt=0.3, cost_llm=0.4, cost_tts=0.2, cost_sms=0.0)
    cc.report(days=7)          # сводка по статьям за неделю
    cc.per_call_avg()          # средняя себестоимость звонка
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "call_cost.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    id            TEXT PRIMARY KEY,
    ts            TEXT NOT NULL,
    phone_hash    TEXT NOT NULL,
    model         TEXT,
    prompt_version TEXT,
    tokens_in     INTEGER DEFAULT 0,
    tokens_out    INTEGER DEFAULT 0,
    tokens_cached INTEGER DEFAULT 0,
    first_voice_ms INTEGER,
    outcome       TEXT,
    test          INTEGER DEFAULT 0,
    duration_sec  INTEGER DEFAULT 0,
    cost_mango    REAL DEFAULT 0,
    cost_stt      REAL DEFAULT 0,
    cost_llm      REAL DEFAULT 0,
    cost_tts      REAL DEFAULT 0,
    cost_sms      REAL DEFAULT 0,
    notes         TEXT
);
CREATE INDEX IF NOT EXISTS idx_calls_ts ON calls(ts);
"""


def phone_hash(phone: str) -> str:
    """Хэш номера (без ПДн в базе)."""
    return hashlib.sha256(phone.encode()).hexdigest()[:16]


class CallCost:
    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def record(self, call_id: str, phone: str = "", **kw) -> None:
        """Записать звонок. phone передавать ПЕРВОНАЧАЛЬНО — внутри хэшируется."""
        row = {
            "id": call_id,
            "ts": datetime.now().isoformat(timespec="seconds"),
            "phone_hash": phone_hash(phone) if phone else kw.pop("phone_hash", ""),
            "model": kw.get("model", ""),
            "prompt_version": kw.get("prompt_version", ""),
            "tokens_in": kw.get("tokens_in", 0),
            "tokens_out": kw.get("tokens_out", 0),
            "tokens_cached": kw.get("tokens_cached", 0),
            "first_voice_ms": kw.get("first_voice_ms"),
            "outcome": kw.get("outcome", ""),
            "test": int(kw.get("test", False)),
            "duration_sec": kw.get("duration_sec", 0),
            "cost_mango": kw.get("cost_mango", 0.0),
            "cost_stt": kw.get("cost_stt", 0.0),
            "cost_llm": kw.get("cost_llm", 0.0),
            "cost_tts": kw.get("cost_tts", 0.0),
            "cost_sms": kw.get("cost_sms", 0.0),
            "notes": json.dumps(kw.get("notes", {}), ensure_ascii=False),
        }
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO calls
                   (id, ts, phone_hash, model, prompt_version, tokens_in, tokens_out,
                    tokens_cached, first_voice_ms, outcome, test, duration_sec,
                    cost_mango, cost_stt, cost_llm, cost_tts, cost_sms, notes)
                   VALUES (:id,:ts,:phone_hash,:model,:prompt_version,:tokens_in,
                    :tokens_out,:tokens_cached,:first_voice_ms,:outcome,:test,
                    :duration_sec,:cost_mango,:cost_stt,:cost_llm,:cost_tts,
                    :cost_sms,:notes)""",
                row,
            )

    def report(self, days: int = 7, include_tests: bool = False) -> dict:
        """Сводка себестоимости за N дней (по статьям, не по звонкам)."""
        since = (
            datetime.now()
            .isoformat(timespec="seconds")
            .replace(datetime.now().strftime("%H:%M:%S"), f"{datetime.now().strftime('%H:%M:%S')}")
        )
        from datetime import timedelta

        since_dt = datetime.now() - timedelta(days=days)
        with self._connect() as conn:
            where = "ts >= ?"
            params: list = [since_dt.isoformat(timespec="seconds")]
            if not include_tests:
                where += " AND test = 0"
            rows = conn.execute(
                f"""SELECT COUNT(*) n,
                    SUM(cost_mango) mango, SUM(cost_stt) stt, SUM(cost_llm) llm,
                    SUM(cost_tts) tts, SUM(cost_sms) sms,
                    SUM(tokens_in) t_in, SUM(tokens_out) t_out, SUM(tokens_cached) t_cached
                    FROM calls WHERE {where}""",
                params,
            ).fetchone()
        total = (
            float(rows["mango"] or 0)
            + float(rows["stt"] or 0)
            + float(rows["llm"] or 0)
            + float(rows["tts"] or 0)
            + float(rows["sms"] or 0)
        )
        return {
            "days": days,
            "calls": rows["n"],
            "cost": {
                "mango": round(rows["mango"] or 0, 4),
                "stt": round(rows["stt"] or 0, 4),
                "llm": round(rows["llm"] or 0, 4),
                "tts": round(rows["tts"] or 0, 4),
                "sms": round(rows["sms"] or 0, 4),
            },
            "tokens": {
                "in": rows["t_in"] or 0,
                "out": rows["t_out"] or 0,
                "cached": rows["t_cached"] or 0,
            },
        }

    def per_call_avg(self, days: int = 7) -> dict:
        rep = self.report(days=days)
        n = rep["calls"] or 1
        total_cost = sum(rep["cost"].values())
        return {"avg_cost_per_call": round(total_cost / n, 4), "calls": rep["calls"]}
