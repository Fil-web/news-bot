from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://zab.ru/news/"
DEFAULT_TIMEOUT = 30
DATA_DIR = Path(__file__).resolve().parents[1] / "database"
JSON_PATH = DATA_DIR / "book.json"
XLSX_PATH = DATA_DIR / "book.xlsx"


def fetch_news_html(timeout: int = DEFAULT_TIMEOUT) -> str:
    response = requests.get(
        BASE_URL,
        timeout=timeout,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        },
    )
    response.raise_for_status()
    return response.text


def parse_news_from_html(src: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(src, "lxml")
    news_cards = soup.find_all("a", class_="zab-news__link-main")

    news_items: list[dict[str, str]] = []
    seen_links: set[str] = set()

    for card in news_cards:
        title_el = card.find("h2", class_="zab-news__title-light")
        date_el = card.find("span", class_="zab-news__info-date")
        description_el = card.find("div", class_="zab-news__description")

        title = title_el.text.strip() if title_el else "Заголовок не указан"
        published_at = date_el.text.strip() if date_el else "Дата не указана"
        description = (
            description_el.text.strip() if description_el else "Описание не указано"
        )
        link = (card.get("href") or "").strip()

        if link and link.startswith("/"):
            link = f"https://zab.ru{link}"
        if not link:
            link = "Ссылка не указана"

        if link in seen_links:
            continue
        seen_links.add(link)

        news_items.append(
            {
                "Заголовок": title,
                "Дата": published_at,
                "Описание": description,
                "Ссылка": link,
            }
        )

    return news_items


def save_news(news_items: list[dict[str, str]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "items": news_items,
        "count": len(news_items),
    }
    JSON_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

    df = pd.DataFrame(news_items)
    df.to_excel(XLSX_PATH, index=False)


def fetch_and_save_news(timeout: int = DEFAULT_TIMEOUT) -> list[dict[str, str]]:
    html = fetch_news_html(timeout=timeout)
    news_items = parse_news_from_html(html)
    save_news(news_items)
    return news_items


if __name__ == "__main__":
    news = fetch_and_save_news()
    print(f"Сохранено новостей: {len(news)}")
