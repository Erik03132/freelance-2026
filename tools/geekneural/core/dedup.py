"""
GeekNeural — ядро дедупликации контекста (token dedup engine).

Один и тот же файл/кусок контекста, запрошенный повторно в рамках сессии,
передаётся модели один раз. При повторном обращении возвращается короткая
ссылка-заглушка вместо полного содержимого -> экономия токенов.

Чистый stdlib (hashlib, sqlite3, json) — без внешних зависимостей.
Используется всеми 4 уровнями: MCP-сервер, shell-hook, браузер, IDE.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Optional

# --- Конфигурация дедупликации ------------------------------------------------

# Файлы/пути, которые НЕЛЬЗЯ дедуплицировать (volatile / real-time / tiny).
# "Где можно урезать расход, а где это нежелательно."
VOLATILE_GLOBS = [
    r"\.log$", r"\.lock$", r"/tmp/", r"/dev/", r"\.pid$",
    r"\.sqlite$", r"\.db$", r"traces\.json$", r"smart_faq_counter\.json$",
    r"run\.log$", r"voice_cached_responses\.json$",
]
VOLATILE_RE = re.compile("|".join(VOLATILE_GLOBS))

# Меньше этого размера (байт) дедупликация невыгодна (накладные > выгода).
MIN_DEDUP_BYTES = 256

# Оценка токенов: ~4 символа на токен для кодовой базы (англ.+символы).
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


@dataclass
class ReadResult:
    content: str
    ref: str
    deduped: bool          # True = отдали ссылку, контент НЕ передавали
    bytes_sent: int
    ref_count: int
    reason: str = ""       # почему deduped / почему нет


@dataclass
class SessionStats:
    reads: int = 0
    deduped: int = 0
    bytes_raw: int = 0          # сколько байт ушло бы без дедупа
    bytes_sent: int = 0         # сколько реально передали
    by_path: dict[str, int] = field(default_factory=dict)

    @property
    def bytes_saved(self) -> int:
        return self.bytes_raw - self.bytes_sent

    @property
    def pct_saved(self) -> float:
        if self.bytes_raw == 0:
            return 0.0
        return 100.0 * self.bytes_saved / self.bytes_raw

    @property
    def est_tokens_saved(self) -> int:
        return self.bytes_saved // CHARS_PER_TOKEN

    def to_dict(self) -> dict:
        return {
            "reads": self.reads,
            "deduped": self.deduped,
            "bytes_raw": self.bytes_raw,
            "bytes_sent": self.bytes_sent,
            "bytes_saved": self.bytes_saved,
            "pct_saved": round(self.pct_saved, 1),
            "est_tokens_saved": self.est_tokens_saved,
            "top_saved_paths": sorted(
                self.by_path.items(), key=lambda kv: kv[1], reverse=True
            )[:10],
        }


class DedupEngine:
    """Content-addressed cache чтений в рамках сессии."""

    def __init__(self, session_id: str, db_path: Optional[str] = None):
        self.session_id = session_id
        if db_path is None:
            base = os.environ.get("GEEKNEURAL_HOME", os.path.expanduser("~/.geekneural"))
            os.makedirs(base, exist_ok=True)
            db_path = os.path.join(base, "cache.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS seen(
                session_id TEXT,
                content_hash TEXT,
                path TEXT,
                size INT,
                ref_count INT DEFAULT 1,
                first_seen REAL,
                PRIMARY KEY (session_id, content_hash)
            )"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS stats(
                session_id TEXT PRIMARY KEY,
                reads INT DEFAULT 0,
                deduped INT DEFAULT 0,
                bytes_raw INT DEFAULT 0,
                bytes_sent INT DEFAULT 0,
                by_path TEXT DEFAULT '{}'
            )"""
        )
        self.conn.commit()
        self.stats = self._load_stats()

    # --- публичный API --------------------------------------------------------

    def _load_stats(self) -> SessionStats:
        cur = self.conn.execute(
            "SELECT reads, deduped, bytes_raw, bytes_sent, by_path "
            "FROM stats WHERE session_id=?", (self.session_id,)
        )
        row = cur.fetchone()
        if not row:
            return SessionStats()
        s = SessionStats(reads=row[0], deduped=row[1], bytes_raw=row[2],
                         bytes_sent=row[3])
        s.by_path = json.loads(row[4]) if row[4] else {}
        return s

    def _save_stats(self) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO stats(session_id, reads, deduped, "
            "bytes_raw, bytes_sent, by_path) VALUES(?,?,?,?,?,?)",
            (self.session_id, self.stats.reads, self.stats.deduped,
             self.stats.bytes_raw, self.stats.bytes_sent,
             json.dumps(self.stats.by_path, ensure_ascii=False)),
        )
        self.conn.commit()

    def read(self, path: str, force: bool = False, label: Optional[str] = None) -> ReadResult:
        """Прочитать файл с дедупликацией.

        При повторном чтении того же содержимого в сессии возвращает короткую
        ссылку (deduped=True), не передавая тело файла.
        """
        self.stats.reads += 1
        label = label or path
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            return ReadResult(
                content=f"[GeekNeural] cannot read {path}: {exc}",
                ref="", deduped=False, bytes_sent=0, ref_count=0,
                reason="read_error",
            )

        raw_bytes = len(content.encode("utf-8"))
        self.stats.bytes_raw += raw_bytes
        chash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        ref = f"gn:{chash}"

        can_dedup = (not force) and self._should_dedup(path, raw_bytes)
        row = self._lookup(chash)

        if can_dedup and row is not None:
            # Уже видели это содержимое -> отдаём ссылку, тело НЕ шлём.
            self.conn.execute(
                "UPDATE seen SET ref_count = ref_count + 1 WHERE "
                "session_id=? AND content_hash=?",
                (self.session_id, chash),
            )
            self.conn.commit()
            self.stats.deduped += 1
            self.stats.bytes_sent += len(ref)  # только ссылка
            self.stats.by_path[label] = self.stats.by_path.get(label, 0) + raw_bytes
            self._save_stats()
            return ReadResult(
                content=f"[GeekNeural] ↺ уже в контексте ({ref}, {raw_bytes}B). "
                        f"Повторная передача пропущена.",
                ref=ref, deduped=True, bytes_sent=len(ref),
                ref_count=row[0] + 1,
                reason="cache_hit",
            )

        # Первый раз (или forced / volatile) -> отдаём полное содержимое.
        self._store(chash, path, raw_bytes)
        self.stats.bytes_sent += raw_bytes
        self._save_stats()
        return ReadResult(
            content=content, ref=ref, deduped=False,
            bytes_sent=raw_bytes, ref_count=1,
            reason="cache_miss" if can_dedup else ("forced" if force else "volatile_or_tiny"),
        )

    def read_text(self, text: str, key: str, force: bool = False) -> ReadResult:
        """Дедупликация произвольного куска текста (не файла). key — стабильный идентификатор."""
        self.stats.reads += 1
        raw_bytes = len(text.encode("utf-8"))
        self.stats.bytes_raw += raw_bytes
        chash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        ref = f"gn:{chash}"
        row = self._lookup(chash)
        if (force is False) and row is not None:
            self.conn.execute(
                "UPDATE seen SET ref_count = ref_count + 1 WHERE "
                "session_id=? AND content_hash=?",
                (self.session_id, chash),
            )
            self.conn.commit()
            self.stats.deduped += 1
            self.stats.bytes_sent += len(ref)
            self.stats.by_path[key] = self.stats.by_path.get(key, 0) + raw_bytes
            self._save_stats()
            return ReadResult(
                content=f"[GeekNeural] ↺ дубликат контекста ({ref}, {raw_bytes}B) пропущен.",
                ref=ref, deduped=True, bytes_sent=len(ref),
                ref_count=row[0] + 1, reason="cache_hit",
            )
        self._store(chash, key, raw_bytes)
        self.stats.bytes_sent += raw_bytes
        self._save_stats()
        return ReadResult(
            content=text, ref=ref, deduped=False, bytes_sent=raw_bytes,
            ref_count=1, reason="cache_miss",
        )

    def stats_dict(self) -> dict:
        return self.stats.to_dict()

    def clear_session(self) -> int:
        cur = self.conn.execute(
            "DELETE FROM seen WHERE session_id=?", (self.session_id,)
        )
        self.conn.execute(
            "DELETE FROM stats WHERE session_id=?", (self.session_id,)
        )
        self.conn.commit()
        n = cur.rowcount
        self.stats = SessionStats()
        return n

    # --- внутреннее -----------------------------------------------------------

    def _should_dedup(self, path: str, size: int) -> bool:
        if size < MIN_DEDUP_BYTES:
            return False
        if VOLATILE_RE.search(path):
            return False
        return True

    def _lookup(self, chash: str):
        cur = self.conn.execute(
            "SELECT ref_count FROM seen WHERE session_id=? AND content_hash=?",
            (self.session_id, chash),
        )
        return cur.fetchone()

    def _store(self, chash: str, path: str, size: int) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO seen(session_id, content_hash, path, size, "
            "ref_count, first_seen) VALUES(?,?,?,?,1,?)",
            (self.session_id, chash, path, size, time.time()),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


def session_from_env() -> str:
    return os.environ.get("GEEKNEURAL_SESSION", "default")
