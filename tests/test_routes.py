import pytest
from unittest.mock import patch
from src.views.routes import generate_main_page, generate_events_page

# Фикстура с фейковыми транзакциями
@pytest.fixture
def mock_transactions():
    return [
        {"date": "2021-12-01 10:00:00", "amount": -1000.0, "category": "Супермаркеты", "description": "Магнит", "card_number": "1111"},
        {"date": "2021-12-15 10:00:00", "amount": 5000.0, "category": "Зарплата", "description": "ООО Ромашка", "card_number": ""},
    ]

# Подменяем load_excel, load_user_settings и API-функции
@patch("src.views.routes.load_excel")
@patch("src.views.routes.load_user_settings")
@patch("src.views.routes.get_currency_rates")
@patch("src.views.routes.get_stock_prices")
def test_generate_main_page(mock_stocks, mock_rates, mock_settings, mock_load, mock_transactions):
    # Настраиваем моки
    mock_load.return_value = mock_transactions
    mock_settings.return_value = {"user_currencies": ["USD"], "user_stocks": []}
    mock_rates.return_value = {"USD": 80.0}
    mock_stocks.return_value = {}

    result = generate_main_page("2021-12-20 12:00:00")

    # Проверяем структуру
    assert "greeting" in result
    assert len(result["cards"]) == 1
    assert result["cards"][0]["last_digits"] == "1111"

    # ПРОВЕРКА ВАЛЮТ (новый формат - список словарей)
    assert isinstance(result["currency_rates"], list)
    assert len(result["currency_rates"]) == 1
    assert result["currency_rates"][0]["currency"] == "USD"
    assert result["currency_rates"][0]["rate"] == 80.0

    # ПРОВЕРКА АКЦИЙ (пустой список, так как mock_stocks вернул {})
    assert isinstance(result["stock_prices"], list)
    assert len(result["stock_prices"]) == 0

@patch("src.views.routes.load_excel")
@patch("src.views.routes.load_user_settings")
@patch("src.views.routes.get_currency_rates")
@patch("src.views.routes.get_stock_prices")
def test_generate_events_page(mock_stocks, mock_rates, mock_settings, mock_load, mock_transactions):
    mock_load.return_value = mock_transactions
    mock_settings.return_value = {"user_currencies": [], "user_stocks": []}
    mock_rates.return_value = {}
    mock_stocks.return_value = {}

    # Вызываем (диапазон 'M' - месяц)
    result = generate_events_page("2021-12-20 12:00:00", range_type='M')

    # Проверяем
    assert "expenses" in result
    assert "income" in result
    # Расходы: -1000, значит total_amount 1000
    assert result["expenses"]["total_amount"] == 1000
    # Доходы: 5000, значит total_amount 5000
    assert result["income"]["total_amount"] == 5000