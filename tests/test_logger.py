import pytest
import logging
import os
from src.utils.logger import setup_logger


def test_setup_logger_creates_file(tmp_path):
    """Проверяем, что логгер создает файл по указанному пути."""
    log_file = tmp_path / "test_sheetbridge.log"

    # Передаем путь как строку
    logger = setup_logger(name="test_logger_1", log_file=str(log_file))

    # Проверяем, что файл физически создался
    assert log_file.exists()

    # Пишем в лог и проверяем, что записалось
    logger.info("Тестовое сообщение")
    content = log_file.read_text(encoding="utf-8")
    assert "Тестовое сообщение" in content


def test_setup_logger_returns_logger():
    """Проверяем, что возвращается объект logging.Logger."""
    logger = setup_logger(name="test_logger_2")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger_2"


def test_setup_logger_no_duplicate_handlers():
    """Проверяем, что повторный вызов не дублирует обработчики."""
    logger1 = setup_logger(name="test_logger_3")
    handlers_count_1 = len(logger1.handlers)

    # Вызываем еще раз
    logger2 = setup_logger(name="test_logger_3")
    handlers_count_2 = len(logger2.handlers)

    # Количество обработчиков не должно измениться (обычно их 2: файл и консоль)
    assert handlers_count_1 == handlers_count_2
    assert handlers_count_1 == 2