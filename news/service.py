from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any

from news.parsing import JSON_PATH, fetch_and_save_news
from utils.logger import logger


class NewsStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._news: list[dict[str, str]] = []
        self._last_updated: datetime | None = None

    async def initialize(self) -> None:
        self._load_cached_news()
        try:
            await self.refresh()
        except Exception as exc:
            if not self._news:
                raise
            logger.warning(
                "Не удалось обновить новости при запуске, используем кеш: %s",
                exc,
            )

    def _load_cached_news(self) -> None:
        if not JSON_PATH.exists():
            logger.info("Кеш новостей не найден, будет выполнен первый парсинг.")
            return

        try:
            payload: Any = json.loads(JSON_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                items = payload.get("items", [])
            else:
                items = payload

            if isinstance(items, list):
                self._news = [item for item in items if isinstance(item, dict)]
                self._last_updated = datetime.fromtimestamp(
                    JSON_PATH.stat().st_mtime,
                    tz=timezone.utc,
                )
                logger.info("Загружено %s новостей из кеша.", len(self._news))
        except Exception as exc:
            logger.warning("Не удалось прочитать кеш новостей: %s", exc)

    async def refresh(self) -> int:
        timeout = int(os.getenv("PARSER_REQUEST_TIMEOUT", "30"))
        async with self._lock:
            news_items = await asyncio.to_thread(fetch_and_save_news, timeout)
            self._news = news_items
            self._last_updated = datetime.now(timezone.utc)
            logger.info("Новости обновлены. Получено %s записей.", len(news_items))
            return len(news_items)

    async def get_news(self) -> list[dict[str, str]]:
        async with self._lock:
            return [item.copy() for item in self._news]

    async def get_news_item(self, index: int) -> dict[str, str] | None:
        async with self._lock:
            if 0 <= index < len(self._news):
                return self._news[index].copy()
            return None

    async def total_news(self) -> int:
        async with self._lock:
            return len(self._news)

    async def get_last_updated(self) -> datetime | None:
        async with self._lock:
            return self._last_updated


news_store = NewsStore()
