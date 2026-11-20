import pytest
import pandas as pd
from unittest.mock import patch
import src.reports.excel_builder as eb


@pytest.fixture
def sample_df():
    """
    Фикстура с тестовым DataFrame.
    - 2021-12-03 (Пятница) -1000 Супермаркеты
    - 2021-12-04 (Суббота) -500 Супермаркеты
    - 2021-12-06 (Понедельник) -200 Такси
    - 2021-08-01 (Старая дата, не должна попасть в отчет) -1000 Супермаркеты
    - 2021-12-10 (Доход, не должен попасть в отчет) 5000 Зарплата
    """
    data = {
        "date": [
            "2021-12-03 12:00:00", "2021-12-04 12:00:00",
            "2021-12-06 12:00:00", "2021-08-01 12:00:00",
            "2021-12-10 12:00:00"
        ],
        "amount": [-1000.0, -500.0, -200.0, -1000.0, 5000.0],
        "category": ["Супермаркеты", "Супермаркеты", "Такси", "Супермаркеты", "Зарплата"],
        "description": ["Магнит", "Пятерочка", "Яндекс", "Лента", "Зарплата"],
        "card_number": ["1111", "1111", "2222", "1111", ""]
    }
    return pd.DataFrame(data)


# ==========================================
# ТЕСТЫ ДЛЯ ДЕКОРАТОРА
# ==========================================
@patch("src.reports.excel_builder.REPORTS_DIR")
def test_report_decorator_saves_file(mock_reports_dir, tmp_path):
    """Проверяем, что декоратор сохраняет файл и возвращает результат."""
    # Подменяем папку сохранения на временную
    mock_reports_dir.__truediv__.return_value = tmp_path / "test_report.xlsx"

    @eb.report_decorator(filename="custom_name.xlsx")
    def dummy_function():
        return pd.DataFrame({"A": [1, 2], "B": [3, 4]})

    # Вызываем функцию
    result = dummy_function()

    # Проверяем, что вернулся DataFrame
    assert isinstance(result, pd.DataFrame)
    # Проверяем, что файл физически создался во временной папке
    assert (tmp_path / "test_report.xlsx").exists()


# ==========================================
# ТЕСТЫ ДЛЯ ОТЧЕТОВ
# ==========================================
# Мы патчим REPORTS_DIR, чтобы декоратор при вызове функций отчетов не создавал реальные файлы
@patch("src.reports.excel_builder.REPORTS_DIR")
def test_spending_by_category(mock_reports_dir, sample_df, tmp_path):
    mock_reports_dir.__truediv__.return_value = tmp_path / "dummy.xlsx"

    # Берем отчет по Супермаркетам на 2021-12-31
    result = eb.spending_by_category(sample_df, "Супермаркеты", date="2021-12-31")

    # Ожидаем: только декабрь 2021, сумма 1000 + 500 = 1500 (отбрасываем старую дату и доходы)
    assert len(result) == 1
    assert result.iloc[0]["month"] == "2021-12"
    assert result.iloc[0]["amount"] == 1500.0


@patch("src.reports.excel_builder.REPORTS_DIR")
def test_spending_by_day_of_week(mock_reports_dir, sample_df, tmp_path):
    mock_reports_dir.__truediv__.return_value = tmp_path / "dummy.xlsx"

    result = eb.spending_by_day_of_week(sample_df, date="2021-12-31")

    # Должно быть 3 дня: Friday (1000), Saturday (500), Monday (200)
    assert len(result) == 3

    # Переводим в словарь для удобства проверки {день: сумма}
    result_dict = dict(zip(result["day_of_week"], result["amount"]))

    assert result_dict["Friday"] == 1000.0
    assert result_dict["Saturday"] == 500.0
    assert result_dict["Monday"] == 200.0


@patch("src.reports.excel_builder.REPORTS_DIR")
def test_spending_by_weekday_or_weekend(mock_reports_dir, sample_df, tmp_path):
    mock_reports_dir.__truediv__.return_value = tmp_path / "dummy.xlsx"

    result = eb.spending_by_weekday_or_weekend(sample_df, date="2021-12-31")

    result_dict = dict(zip(result["day_type"], result["amount"]))

    # Рабочие дни: Friday (1000) + Monday (200) = 1200. Среднее = 1200 / 2 = 600.
    assert result_dict["Рабочие"] == 600.0

    # Выходные: Saturday (500) = 500. Среднее = 500 / 1 = 500.
    assert result_dict["Выходные"] == 500.0