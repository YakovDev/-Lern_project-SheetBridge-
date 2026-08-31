def report_decorator(filename: str = None):
    """Декоратор для записи результата отчётной функции в Excel-файл."""
    # (декоратор – это функция, возвращающая обёртку)

@report_decorator()
def spending_by_category(df, category: str, date: str = None) -> dict:
    """Траты по категории за последние 3 месяца (от date или от текущей)."""

@report_decorator()
def spending_by_day_of_week(df, date: str = None) -> dict:
    """Средние траты по дням недели за последние 3 месяца."""

@report_decorator()
def spending_by_weekday_or_weekend(df, date: str = None) -> dict:
    """Средние траты в рабочие и выходные дни за последние 3 месяца."""