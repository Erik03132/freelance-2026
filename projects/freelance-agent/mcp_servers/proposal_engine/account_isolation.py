"""
Инвариант изоляции аккаунтов для multi-account агентов.

Принцип: данные = (адрес сервера + account_id).
Чистка кэшей при смене пользователя.
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AccountContext:
    account_id: str
    platform: str
    server_host: str = ""
    cache_dir: Optional[Path] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def cache_key(self) -> str:
        raw = f"{self.server_host}:{self.account_id}:{self.platform}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class AccountIsolator:
    """
    Гарантирует, что данные одного аккаунта не попадают в сессию другого.

    Инварианты:
      1. cache_dir уникален для каждого аккаунта
      2. При смене аккаунта — полная очистка кэшей
      3. Файлы сессий привязаны к account_id (не глобальные)
    """

    def __init__(self, base_cache_dir: Optional[Path] = None):
        self._base_cache = base_cache_dir or Path.home() / ".cache" / "freelance-agent"
        self._active: Optional[AccountContext] = None
        self._contexts: dict[str, AccountContext] = {}

    def register(self, ctx: AccountContext) -> Path:
        cache_dir = self._base_cache / ctx.platform / ctx.cache_key
        cache_dir.mkdir(parents=True, exist_ok=True)
        ctx.cache_dir = cache_dir
        self._contexts[ctx.cache_key] = ctx
        logger.info("Registered account %s on %s → %s", ctx.account_id, ctx.platform, cache_dir)
        return cache_dir

    def switch(self, account_id: str, platform: str) -> AccountContext:
        ctx = self._find(account_id, platform)
        if self._active and self._active.cache_key != ctx.cache_key:
            self._purge_caches(self._active)
            logger.info("Switched from %s to %s", self._active.account_id, account_id)
        self._active = ctx
        return ctx

    def _find(self, account_id: str, platform: str) -> AccountContext:
        for ctx in self._contexts.values():
            if ctx.account_id == account_id and ctx.platform == platform:
                return ctx
        ctx = AccountContext(account_id=account_id, platform=platform)
        self.register(ctx)
        return ctx

    def _purge_caches(self, ctx: AccountContext) -> None:
        cache_dir = ctx.cache_dir or self._base_cache / ctx.platform / ctx.cache_key
        if not cache_dir.exists():
            return
        for item in cache_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                import shutil
                shutil.rmtree(item)
        logger.info("Purged cache for account %s: %s", ctx.account_id, cache_dir)

    def verify_isolation(self) -> list[str]:
        """Проверяет, что кэш-директории не пересекаются между аккаунтами."""
        violations: list[str] = []
        dirs = []
        for ctx in self._contexts.values():
            if ctx.cache_dir and ctx.cache_dir.exists():
                dirs.append((ctx.cache_key, ctx.cache_dir.resolve()))
        for i in range(len(dirs)):
            for j in range(i + 1, len(dirs)):
                if dirs[i][1] == dirs[j][1]:
                    violations.append(f"Overlap: {dirs[i][0]} == {dirs[j][0]}")
        return violations

    def get_active_context(self) -> Optional[AccountContext]:
        return self._active

    def dump_manifes(self) -> dict:
        return {
            ctx.cache_key: {
                "account_id": ctx.account_id,
                "platform": ctx.platform,
                "server_host": ctx.server_host,
                "cache_dir": str(ctx.cache_dir) if ctx.cache_dir else None,
            }
            for ctx in self._contexts.values()
        }
