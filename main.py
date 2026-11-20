import argparse
import datetime
import json
from pathlib import Path
import logging

from src.utils.logger import setup_logger

from src.services.loader import load_excel, XLSX_FILE
from src.services.services import export_to_json, export_to_excel
from src.views.routes import generate_main_page, generate_events_page


def main():
    """Точка входа CLI для генерации отчетов."""
    setup_logger()  # <--- Включаем логирование
    logger = logging.getLogger("sheetbridge")
    parser = argparse.ArgumentParser(description="SheetBridge ETL-приложение")
    parser.add_argument(
        "--date",
        type=str,
        default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        help="Дата и время для отчета (формат: YYYY-MM-DD HH:MM:SS)"
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="data/output/result.json",
        help="Путь для сохранения итогового JSON"
    )
    parser.add_argument(
        "--output-excel",
        type=str,
        default="data/output/report.xlsx",
        help="Путь для сохранения Excel-отчета"
    )

    args = parser.parse_args()

    logger.info(f"Запуск генерации для даты: {args.date}")

    # 1. Загружаем исходные данные
    transactions = load_excel(XLSX_FILE)
    if not transactions:
        logger.error("Данные не загружены. Проверьте файл Excel.")
        return

    # 2. Генерируем JSON для главной страницы
    logger.info("Формирование данных для главной страницы...")
    main_page_data = generate_main_page(args.date)

    # 3. Генерируем JSON для страницы событий
    logger.info("Формирование данных для страницы событий...")
    events_page_data = generate_events_page(args.date, range_type='M')

    # Объединяем оба ответа в один итоговый словарь (или можно сохранять по отдельности)
    final_json = {
        "main_page": main_page_data,
        "events_page": events_page_data
    }

    # 4. Экспорт в JSON
    logger.info(f"Сохранение JSON в {args.output_json}...")
    export_to_json(final_json, args.output_json)

    # 5. Экспорт в Excel (сохраняем статистику событий как пример)
    logger.info(f"Сохранение Excel в {args.output_excel}...")
    export_to_excel(events_page_data["expenses"], args.output_excel)

    logger.info("Готово! Все файлы успешно созданы.")


if __name__ == "__main__":
    main()