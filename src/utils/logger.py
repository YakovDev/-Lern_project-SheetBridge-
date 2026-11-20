"""
Настройка логирования для проекта SheetBridge.
"""

import logging
import sys
from pathlib import Path

# Корень проекта: logger.py -> utils -> src -> SheetBridge
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"


def setup_logger(name: str = "sheetbridge", log_file: str = None) -> logging.Logger:
    """
    Настраивает и возвращает логгер с выводом в файл и консоль.

    Аргументы:
        name: имя логгера (по умолчанию "sheetbridge").
        log_file: путь к файлу лога. Если не указан — logs/sheetbridge.log.

    Возвращает:
        Настроенный объект logging.Logger.
    """
    # Если файл не указан — берем путь по умолчанию от корня проекта
    if log_file is None:
        log_file = LOGS_DIR / "sheetbridge.log"
    else:
        log_file = Path(log_file)

    # Создаем папку для логов, если ее нет
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Создаем (или получаем существующий) логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Если логгер уже настроен (например, при повторном вызове), не дублируем хендлеры
    if logger.handlers:
        return logger

    # --- Форматтер (как будет выглядеть строка лога) ---
    # Пример: 2026-11-14 15:30:00 | INFO     | sheetbridge | Сообщение
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Обработчик для файла (пишет всё от DEBUG и выше) ---
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # --- Обработчик для консоли (пишет только INFO и выше) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # --- Добавляем обработчики к логгеру ---
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger