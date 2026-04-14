from __future__ import annotations

import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "bot.log"


def setup_logging() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("news_bot")
    logger.info("Логирование настроено.")
    return logger


logger = setup_logging()
