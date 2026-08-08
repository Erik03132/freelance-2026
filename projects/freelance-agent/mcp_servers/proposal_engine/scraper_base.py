"""
Модуль скрапинга с паттерном "рецепт + фолбэк".
Реализует двухслойный извлекатель для freelance-агента:
  - Серверный профиль-контракт (быстрый HTTP-путь)
  - Локальный рецепт-фолбэк (Playwright при 403)

Принцип: 403-проблема не в селекторе, а в окружении.
Быстрый путь не маскирует поломку — автоматически восстанавливается.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ScrapeError(Exception):
    pass


class ScrapeForbidden(ScrapeError):
    """HTTP 403 — окружение (IP/прокси/сессия) отбраковано платформой."""


class ScrapeTimeout(ScrapeError):
    pass


class ScrapeRetryable(ScrapeError):
    """Временная ошибка, можно повторить."""


@dataclass
class ScrapeRecipe:
    """Контракт быстрого пути: HTTP-запрос с селекторами."""
    name: str
    url: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    selector: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "selector": self.selector,
        }


@dataclass
class ScrapeResult:
    success: bool
    content: str = ""
    status_code: int = 0
    method: str = "http"
    error: str = ""
    elapsed_ms: float = 0.0

    def is_forbidden(self) -> bool:
        return self.status_code in (403, 429)

    def is_retryable(self) -> bool:
        return self.status_code >= 500 or self.status_code == 429


class EnvironmentSwitcher(ABC):
    """Меняет окружение при 403: прокси → IP → сессия — не селекторы."""

    def __init__(self, account_id: str = ""):
        self.account_id = account_id
        self._proxies: list[str] = []
        self._proxy_index: int = -1
        self._session_rotations: int = 0
        self.max_proxy_rotations: int = 3
        self.max_session_rotations: int = 2

    def set_proxies(self, proxies: list[str]) -> None:
        self._proxies = proxies
        self._proxy_index = -1

    def rotate_proxy(self) -> Optional[str]:
        if not self._proxies:
            return None
        self._proxy_index = (self._proxy_index + 1) % len(self._proxies)
        if self._proxy_index == 0 and self._proxy_index > 0:
            self._proxy_index = 0
        if self._proxy_index >= self.max_proxy_rotations * len(self._proxies):
            return None
        return self._proxies[self._proxy_index % len(self._proxies)]

    def rotate_session(self) -> bool:
        if self._session_rotations >= self.max_session_rotations:
            return False
        self._session_rotations += 1
        self._on_session_rotate()
        return True

    def reset(self) -> None:
        self._proxy_index = -1
        self._session_rotations = 0

    @abstractmethod
    def _on_session_rotate(self) -> None:
        """Очистка кэшей, пересоздание сессии."""


class TwoLayerExtractor:
    """
    Двухслойный извлекатель:
      1. Быстрый путь — HTTP + рецепт
      2. Фолбэк — Playwright (полный браузер)
    При 403 автоматически переключает окружение (прокси/IP/сессию),
    а НЕ подбирает селекторы.
    """

    def __init__(
        self,
        env_switcher: Optional[EnvironmentSwitcher] = None,
        fast_http: Optional[Callable[[ScrapeRecipe], ScrapeResult]] = None,
        playwright_fetch: Optional[Callable[[ScrapeRecipe], ScrapeResult]] = None,
    ):
        self.env = env_switcher or EnvironmentSwitcher()
        self._fast_http = fast_http
        self._playwright_fetch = playwright_fetch
        self._stats: dict[str, int] = {"http_hits": 0, "http_403s": 0, "playwright_fallbacks": 0}

    async def extract(self, recipe: ScrapeRecipe) -> ScrapeResult:
        """Основной метод: быстрый путь → окружение → фолбэк."""
        self.env.reset()
        t0 = time.monotonic()

        result = await self._try_http(recipe)
        if result.success:
            result.elapsed_ms = (time.monotonic() - t0) * 1000
            self._stats["http_hits"] += 1
            return result

        if not result.is_forbidden():
            result.elapsed_ms = (time.monotonic() - t0) * 1000
            return result

        self._stats["http_403s"] += 1
        logger.warning("403 on %s — rotating environment, not selectors", recipe.url)

        for _ in range(self.env.max_proxy_rotations):
            proxy = self.env.rotate_proxy()
            if proxy:
                recipe.headers = {**recipe.headers, "X-Proxy": proxy}
                result = await self._try_http(recipe)
                if result.success:
                    result.elapsed_ms = (time.monotonic() - t0) * 1000
                    return result
                if not result.is_forbidden():
                    break

        if self.env.rotate_session():
            result = await self._try_http(recipe)
            if result.success:
                result.elapsed_ms = (time.monotonic() - t0) * 1000
                return result

        result = await self._fallback_playwright(recipe)
        result.elapsed_ms = (time.monotonic() - t0) * 1000
        return result

    async def _try_http(self, recipe: ScrapeRecipe) -> ScrapeResult:
        if self._fast_http:
            return self._fast_http(recipe)
        return ScrapeResult(success=False, error="No HTTP handler configured")

    async def _fallback_playwright(self, recipe: ScrapeRecipe) -> ScrapeResult:
        self._stats["playwright_fallbacks"] += 1
        logger.info("Falling back to Playwright for %s", recipe.url)
        if self._playwright_fetch:
            return self._playwright_fetch(recipe)
        return ScrapeResult(success=False, method="playwright", error="No Playwright handler configured")

    def stats(self) -> dict[str, int]:
        return dict(self._stats)
