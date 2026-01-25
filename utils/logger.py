# logger.py
import logging
import os

# Настройка логирования
def setup_logging():
    """
    Настройка логирования.
    Логи записываются в файл bot.log.
    """
    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат логов
        handlers=[
            logging.FileHandler("utils/test.log"),  # Записываем логи в файл
            logging.StreamHandler()  # Выводим логи в консоль (опционально)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Логирование настроено.")
    return logger

# Инициализация логгера
logger = setup_logging()