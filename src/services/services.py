# ------------------------------------------------------------
# Трансформация (бывший transformer.py)
# ------------------------------------------------------------
def transform_data(transactions: list[dict]) -> list[dict]:
    """Очищает и нормализует данные: даты, суммы, категории."""

def get_card_summary(transactions: list[dict]) -> dict:
    """
    Группирует расходы по картам (последние 4 цифры).
    Возвращает { "1234": {"spent": 1000.0, "cashback": 10.0}, ... }.
    """

def get_top_transactions(transactions: list[dict], n: int = 5) -> list[dict]:
    """Возвращает топ-N транзакций по сумме расхода."""

def get_category_spending(transactions: list[dict], top_n: int = 7) -> dict:
    """
    Группирует расходы по категориям. Топ-N категорий + категория "Остальное".
    Возвращает {"Категория": сумма, ...}.
    """

def get_income_expense(transactions: list[dict]) -> dict:
    """
    Считает общие суммы доходов и расходов, разбивает по категориям.
    Возвращает {'income': {'total': float, 'categories': {...}},
               'expense': {'total': float, 'categories': {...}}}
    """

def filter_by_phone(transactions: list[dict]) -> list[dict]:
    """Возвращает транзакции, в описании которых есть номер телефона (регулярка)."""

def filter_transfers_to_individuals(transactions: list[dict]) -> list[dict]:
    """Возвращает переводы физлицам (категория 'Переводы' + описание вида 'Имя Ф.')."""

# ------------------------------------------------------------
# Экспорт и внешние API (бывший exporter.py)
# ------------------------------------------------------------
def export_to_json(data: dict, file_path: str) -> None:
    """Сохраняет словарь в JSON-файл."""

def export_to_excel(data: dict, file_path: str, template: str = None) -> None:
    """Генерирует Excel-отчёт с группировками и форматированием."""

def get_currency_rates(currencies: list[str]) -> dict:
    """Возвращает текущие курсы валют (к рублю) через внешнее API."""

def get_stock_prices(stocks: list[str]) -> dict:
    """Возвращает текущие цены акций через внешнее API."""

# ------------------------------------------------------------
# Сервисы из ТЗ (анализ кешбэка, инвесткопилка, поиск)
# ------------------------------------------------------------
def cashback_analysis(data: list[dict], year: int, month: int) -> dict:
    """
    Анализирует выгодные категории повышенного кешбэка.
    Возвращает {"Категория": возможный кешбэк, ...}.
    """

def investment_bank(month: str, transactions: list[dict], limit: int) -> float:
    """
    Рассчитывает накопления по правилу «Инвесткопилка» за указанный месяц.
    month – 'YYYY-MM'.
    limit – шаг округления (10, 50, 100).
    """

def search_transactions(query: str, transactions: list[dict]) -> list[dict]:
    """Возвращает транзакции, содержащие query в описании или категории."""

def search_by_phone(transactions: list[dict]) -> list[dict]:
    """Возвращает транзакции с мобильными номерами в описании (использует регулярку)."""

def search_transfers_to_individuals(transactions: list[dict]) -> list[dict]:
    """Возвращает транзакции переводов физлицам (категория 'Переводы' + 'Имя Ф.')."""