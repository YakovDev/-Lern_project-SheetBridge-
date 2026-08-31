# --- Трансформация ---
def test_transform_data() -> None:
    """Проверяет, что transform_data очищает даты, суммы и категории."""
    pass

def test_get_card_summary() -> None:
    """Проверяет расчёт расходов и кешбэка по картам."""
    pass

def test_get_top_transactions() -> None:
    """Проверяет, что возвращаются топ-N транзакций по убыванию суммы."""
    pass

def test_get_category_spending() -> None:
    """Проверяет группировку расходов по категориям с учётом топ-N и 'Остальное'."""
    pass

def test_get_income_expense() -> None:
    """Проверяет разделение доходов и расходов с разбивкой по категориям."""
    pass

def test_filter_by_phone() -> None:
    """Проверяет фильтрацию транзакций с номерами телефонов в описании."""
    pass

def test_filter_transfers_to_individuals() -> None:
    """Проверяет фильтрацию переводов физлицам (категория 'Переводы' + 'Имя Ф.')."""
    pass

# --- Экспорт и внешние API ---
def test_export_to_json() -> None:
    """Проверяет, что export_to_json создаёт корректный JSON-файл."""
    pass

def test_export_to_excel() -> None:
    """Проверяет, что export_to_excel создаёт Excel-файл с нужными листами и форматированием."""
    pass

def test_get_currency_rates() -> None:
    """Проверяет получение курсов валют (можно использовать mock для API)."""
    pass

def test_get_stock_prices() -> None:
    """Проверяет получение цен акций (с mock-запросами)."""
    pass

# --- Сервисы (кешбэк, инвесткопилка, поиск) ---
def test_cashback_analysis() -> None:
    """Проверяет расчёт потенциального кешбэка по категориям за указанный месяц."""
    pass

def test_investment_bank() -> None:
    """Проверяет сумму накоплений по правилу инвесткопилки для заданного месяца."""
    pass

def test_search_transactions() -> None:
    """Проверяет поиск транзакций по подстроке в описании или категории."""
    pass

def test_search_by_phone() -> None:
    """Проверяет поиск транзакций с мобильными номерами."""
    pass

def test_search_transfers_to_individuals() -> None:
    """Проверяет поиск переводов физлицам."""
    pass