import pytest
import json
import math
import pandas as pd
from unittest.mock import patch
from src.services.services import (
    get_card_summary, get_top_transactions, get_category_spending,
    get_income_expense, filter_by_phone, filter_transfers_to_individuals,
    export_to_json, export_to_excel, search_transactions,
    get_currency_rates, get_stock_prices, cashback_analysis, investment_bank
)


# ==========================================
# ФИКСТУРЫ
# ==========================================
@pytest.fixture
def sample_transactions():
    return [
        {"date": "2021-12-01 10:00:00", "amount": -1000.0, "category": "Супермаркеты", "description": "Магнит",
         "card_number": "1111"},
        {"date": "2021-12-02 11:00:00", "amount": -500.0, "category": "Супермаркеты", "description": "Пятерочка",
         "card_number": "1111"},
        {"date": "2021-12-03 12:00:00", "amount": -200.0, "category": "Такси", "description": "Яндекс",
         "card_number": "2222"},
        {"date": "2021-12-04 13:00:00", "amount": -50.0, "category": "Такси", "description": "Ситимобил",
         "card_number": "2222"},
        {"date": "2021-12-05 14:00:00", "amount": -1500.0, "category": "Электроника", "description": "DNS",
         "card_number": "1111"},
        {"date": "2021-12-06 15:00:00", "amount": 5000.0, "category": "Зарплата", "description": "ООО Ромашка",
         "card_number": ""},
    ]


# ==========================================
# 1. АНАЛИТИКА (Карты, Топ, Категории)
# ==========================================
def test_get_card_summary(sample_transactions):
    result = get_card_summary(sample_transactions)
    assert result["1111"] == {"spent": 3000.0, "cashback": 30.0}
    assert result["2222"] == {"spent": 250.0, "cashback": 2.5}

    # Пустой список и список без расходов
    assert get_card_summary([]) == {}
    assert get_card_summary([{"amount": 100, "card_number": "1"}]) == {}


def test_get_top_transactions(sample_transactions):
    result = get_top_transactions(sample_transactions, n=2)
    assert len(result) == 2
    assert result[0]["amount"] == -1500.0
    assert result[1]["amount"] == -1000.0
    assert get_top_transactions([]) == []


def test_get_category_spending(sample_transactions):
    # С "Остальным"
    result = get_category_spending(sample_transactions, top_n=2)
    assert result["Электроника"] == 1500.0
    assert result["Супермаркеты"] == 1500.0
    assert result["Остальное"] == 250.0

    # Без "Остального" (все влезли)
    result_all = get_category_spending(sample_transactions, top_n=10)
    assert "Остальное" not in result_all

    # Без категорий (None/пустые)
    tx_no_cat = [{"amount": -100, "category": None}, {"amount": -50}]
    assert get_category_spending(tx_no_cat) == {"Неизвестно": 150.0}
    assert get_category_spending([]) == {}


def test_get_income_expense(sample_transactions):
    result = get_income_expense(sample_transactions)
    assert result["income"]["total"] == 5000.0
    assert result["expense"]["total"] == 3250.0

    # Проверка на пустые категории
    tx = [{"amount": 100}, {"amount": -50}]
    res_none = get_income_expense(tx)
    assert res_none["income"]["categories"]["Неизвестно"] == 100
    assert res_none["expense"]["categories"]["Неизвестно"] == 50

    assert get_income_expense([]) == {
        "expense": {"total": 0, "categories": {}},
        "income": {"total": 0, "categories": {}}
    }


# ==========================================
# 2. ПОИСК
# ==========================================
def test_filter_by_phone():
    tx = [
        {"description": "Я МТС +7 921 11-22-33"},
        {"description": "Магнит"},
        {"description": None},
        {}
    ]
    assert len(filter_by_phone(tx)) == 1


def test_filter_transfers_to_individuals():
    tx = [
        {"category": "Переводы", "description": "Валерий А."},
        {"category": "Переводы", "description": "ООО Ромашка"},
        {"category": "Супермаркеты", "description": "Сергей З."},
        {"category": "Переводы", "description": None},
        {"category": "Переводы"}
    ]
    assert len(filter_transfers_to_individuals(tx)) == 1


def test_search_transactions(sample_transactions):
    assert len(search_transactions("магнит", sample_transactions)) == 1
    assert len(search_transactions("ТАКСИ", sample_transactions)) == 2

    # Проверка на None в полях
    tx = [{"description": None, "category": None}, {"description": "Магнит"}]
    assert len(search_transactions("магнит", tx)) == 1
    assert len(search_transactions("xyz", sample_transactions)) == 0


# ==========================================
# 3. ЭКСПОРТ
# ==========================================
def test_export_to_json(tmp_path):
    file_path = tmp_path / "test.json"
    test_data = {"a": 1, "b": "Привет"}
    export_to_json(test_data, file_path)
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        assert json.load(f) == test_data


def test_export_to_excel(tmp_path, sample_transactions):
    # Ветка 1: Пустой словарь
    f_empty = tmp_path / "empty.xlsx"
    export_to_excel({}, f_empty)
    assert pd.read_excel(f_empty).iloc[0, 0] == "Нет данных для отчёта"

    # Ветка 2: Плоский словарь
    f_flat = tmp_path / "flat.xlsx"
    export_to_excel({"A": 1, "B": 2}, f_flat)
    assert len(pd.read_excel(f_flat)) == 2

    # Ветка 3: Карты (spent/cashback)
    f_cards = tmp_path / "cards.xlsx"
    export_to_excel(get_card_summary(sample_transactions), f_cards)
    assert "Карта" in pd.read_excel(f_cards).columns

    # Ветка 4: Доходы/расходы (с ключом categories)
    f_inc_exp = tmp_path / "inc_exp.xlsx"
    export_to_excel(get_income_expense(sample_transactions), f_inc_exp)
    assert len(pd.ExcelFile(f_inc_exp).sheet_names) == 2

    # Ветка 5: Вложенный словарь БЕЗ ключа categories (elif isinstance)
    f_nested = tmp_path / "nested.xlsx"
    export_to_excel({"custom": {"key": "value"}}, f_nested)
    assert f_nested.exists()


# ==========================================
# 4. ВНЕШНИЕ API (С моками)
# ==========================================
@patch("src.services.services.requests.get")
def test_get_currency_rates(mock_get):
    # Успешный ответ. Проверяем игнорирование нулевого курса.
    mock_get.return_value.json.return_value = {"rates": {"USD": 0.012, "EUR": 0}}
    result = get_currency_rates(["USD", "EUR", "GBP"])  # GBP нет в ответе
    assert result["USD"] == 83.33
    assert "EUR" not in result

    # Ошибка (Exception)
    mock_get.side_effect = Exception("Network Error")
    assert get_currency_rates(["USD"]) == {}


@patch("src.services.services.requests.get")
def test_get_stock_prices(mock_get):
    # Успешный ответ
    mock_get.return_value.json.return_value = {
        "chart": {"result": [{"meta": {"regularMarketPrice": 150.5}}]}
    }
    assert get_stock_prices(["AAPL"]) == {"AAPL": 150.5}

    # Ответ без данных (chart = None)
    mock_get.return_value.json.return_value = {"chart": {"result": None}}
    assert get_stock_prices(["AAPL"]) == {}

    # Ответ без цены (price = None)
    mock_get.return_value.json.return_value = {"chart": {"result": [{"meta": {}}]}}
    assert get_stock_prices(["AAPL"]) == {}

    # Ошибка запроса
    mock_get.side_effect = Exception("Network Error")
    assert get_stock_prices(["AAPL"]) == {}


# ==========================================
# 5. СЕРВИСЫ ИЗ ТЗ (Кешбэк, Инвесткопилка)
# ==========================================
def test_cashback_analysis(sample_transactions):
    # Добавим транзакции, чтобы было больше 3 категорий для проверки сортировки
    tx = sample_transactions + [
        {"date": "2021-12-07", "amount": -5000.0, "category": "ЖКХ"}
    ]
    result = cashback_analysis(tx, 2021, 12)

    # Теперь возвращается список словарей
    assert isinstance(result, list)
    assert len(result) == 3  # Должно вернуться ровно 3 категории (Топ-3)

    # Самая большая категория - ЖКХ (5000 / 100 = 50.0)
    assert result[0]["category"] == "ЖКХ"
    assert result[0]["cashback"] == 50.0

    # Некорректные даты (проверка try/except)
    bad_dates = [
        {"amount": -100, "date": ""},
        {"amount": -100, "date": "abc-12-01"},
        {"amount": -100, "date": "2021"},
        {"amount": -100}
    ]
    assert cashback_analysis(bad_dates, 2021, 12) == []


def test_investment_bank():
    tx = [
        {"date": "2021-12-01 10:00:00", "amount": -1712.0},  # 38
        {"date": "2021-12-02 10:00:00", "amount": 500.0},  # Доход (игнорируется)
        {"date": "2021-11-01 10:00:00", "amount": -100.0},  # Не тот месяц
    ]
    assert investment_bank("2021-12", tx, 50) == 38.0