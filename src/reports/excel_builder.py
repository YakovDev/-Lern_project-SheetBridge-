import pandas as pd
import datetime
from functools import wraps
from pathlib import Path
import logging

logger = logging.getLogger("sheetbridge")
# Путь для сохранения отчетов по умолчанию
BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "data" / "output"


def report_decorator(filename: str = None):
    """
    Декоратор для функций-отчетов. 
    Если filename не указан, генерирует имя автоматически на основе имени функции и текущей даты.
    Сохраняет результат работы функции (DataFrame) в Excel-файл.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Вызываем функцию и получаем результат
            result = func(*args, **kwargs)

            # 2. Определяем имя файла
            if filename:
                file_path = REPORTS_DIR / filename
            else:
                # Автоматическое имя: report_название_функции_ГГГГ-ММ-ДД.xlsx
                today = datetime.date.today().strftime("%Y-%m-%d")
                auto_name = f"report_{func.__name__}_{today}.xlsx"
                file_path = REPORTS_DIR / auto_name

            # 3. Создаем папку, если ее нет
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 4. Сохраняем в Excel (если результат - DataFrame или словарь)
            if isinstance(result, pd.DataFrame):
                result.to_excel(file_path, index=False, engine="openpyxl")
            elif isinstance(result, dict):
                pd.DataFrame(list(result.items()), columns=["Ключ", "Значение"]).to_excel(file_path, index=False)

            logger.info(f"Отчет сохранен в файл: {file_path}")

            # Возвращаем результат, чтобы его можно было использовать дальше в коде
            return result

        return wrapper

    return decorator


def _prepare_data(transactions: pd.DataFrame, date: str = None) -> pd.DataFrame:
    """
    Вспомогательная функция (не по ТЗ, для удобства).
    Фильтрует расходы за последние 3 месяца от указанной даты.
    """
    # 1. Определяем конечную дату (сегодня или переданную)
    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = pd.Timestamp.today()

    # 2. Начальная дата - ровно 3 месяца назад
    start_date = end_date - pd.DateOffset(months=3)

    # 3. Приводим колонку date к формату datetime (на всякий случай)
    df = transactions.copy()
    df["date"] = pd.to_datetime(df["date"])

    # 4. Фильтруем: только расходы (amount < 0) и только за последние 3 месяца
    mask = (df["amount"] < 0) & (df["date"] >= start_date) & (df["date"] <= end_date)
    filtered_df = df[mask].copy()

    # 5. Делаем суммы положительными для удобства отчетов
    filtered_df["amount"] = filtered_df["amount"].abs()

    return filtered_df


@report_decorator()
def spending_by_category(df: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
    """
    Траты по заданной категории за последние 3 месяца.
    """
    # 1. Подготавливаем данные (расходы за 3 месяца)
    filtered_df = _prepare_data(df, date)

    # 2. Фильтруем по нужной категории
    cat_df = filtered_df[filtered_df["category"] == category].copy()

    # 3. Группируем по месяцам
    cat_df["month"] = cat_df["date"].dt.to_period("M").astype(str)
    result = cat_df.groupby("month")["amount"].sum().reset_index()

    return result


@report_decorator()
def spending_by_day_of_week(df: pd.DataFrame, date: str = None) -> pd.DataFrame:
    """
    Средние траты по дням недели за последние 3 месяца.
    """
    filtered_df = _prepare_data(df, date)

    # 1. Получаем название дня недели (Monday, Tuesday...)
    filtered_df["day_of_week"] = filtered_df["date"].dt.day_name()

    # 2. Группируем и считаем среднее
    result = filtered_df.groupby("day_of_week")["amount"].mean().reset_index()
    result["amount"] = result["amount"].round(2)

    return result


@report_decorator()
def spending_by_weekday_or_weekend(df: pd.DataFrame, date: str = None) -> pd.DataFrame:
    """
    Средние траты в рабочие и выходные дни за последние 3 месяца.
    """
    filtered_df = _prepare_data(df, date)

    # 1. Определяем выходной (5 - суббота, 6 - воскресенье)
    filtered_df["is_weekend"] = filtered_df["date"].dt.weekday >= 5

    # 2. Заменяем True/False на понятный текст
    filtered_df["day_type"] = filtered_df["is_weekend"].map({True: "Выходные", False: "Рабочие"})

    # 3. Группируем и считаем среднее
    result = filtered_df.groupby("day_type")["amount"].mean().reset_index()
    result["amount"] = result["amount"].round(2)

    return result