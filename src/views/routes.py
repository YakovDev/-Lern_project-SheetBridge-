import datetime
from src.services.services import (
    get_card_summary,
    get_top_transactions,
    get_income_expense,
    get_currency_rates,
    get_stock_prices,
)
from src.services.configs import load_user_settings
from src.services.loader import load_excel, XLSX_FILE


def _get_greeting() -> str:
    """Возвращает приветствие в зависимости от текущего времени."""
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def _filter_by_date(transactions: list[dict], start_date: str, end_date: str) -> list[dict]:
    """
    Фильтрует транзакции по строковому диапазону дат.
    Формат дат: 'YYYY-MM-DD HH:MM:SS' или 'YYYY-MM-DD' (строковое сравнение работает корректно).
    """
    filtered = []
    for t in transactions:
        t_date = t.get("date", "")
        if start_date <= t_date <= end_date:
            filtered.append(t)
    return filtered


def generate_main_page(date_str: str) -> dict:
    """
    Главная страница.
    Принимает 'YYYY-MM-DD HH:MM:SS'.
    Возвращает JSON с приветствием, картами, топ-5, курсами, акциями.
    """
    # 1. Загружаем данные
    transactions = load_excel(XLSX_FILE)
    settings = load_user_settings()

    # 2. Получаем валюты и акции (преобразуем в списки словарей)
    raw_rates = get_currency_rates(settings.get("user_currencies", []))
    currency_rates = [{"currency": k, "rate": v} for k, v in raw_rates.items()]

    raw_stocks = get_stock_prices(settings.get("user_stocks", []))
    stock_prices = [{"stock": k, "price": v} for k, v in raw_stocks.items()]

    # 3. Определяем диапазон: с 1-го числа месяца по входящую дату
    dt = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d")
    start_of_month = dt.replace(day=1).strftime("%Y-%m-%d 00:00:00")

    # 4. Фильтруем данные
    filtered_data = _filter_by_date(transactions, start_of_month, date_str)

    # 5. Собираем компоненты
    greeting = _get_greeting()
    cards = get_card_summary(filtered_data)
    top_5 = get_top_transactions(filtered_data, n=5)

    # 6. Форматируем дату в топ-5 под стандарт dd.mm.yyyy
    top_5_formatted = []
    for t in top_5:
        date_obj = datetime.datetime.strptime(t["date"][:10], "%Y-%m-%d")
        top_5_formatted.append({
            "date": date_obj.strftime("%d.%m.%Y"),
            "amount": t["amount"],
            "category": t["category"],
            "description": t["description"]
        })

    # 7. Преобразуем данные по картам в нужный формат списка
    cards_list = [
        {"last_digits": card, "total_spent": info["spent"], "cashback": info["cashback"]}
        for card, info in cards.items() if card  # пропускаем пустые карты
    ]

    # 8. Возвращаем итоговый JSON
    return {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_5_formatted,
        "currency_rates": currency_rates,  # <-- Теперь это список
        "stock_prices": stock_prices,      # <-- Теперь это список
    }

def generate_events_page(date_str: str, range_type: str = 'M') -> dict:
    """
    Страница событий.
    Принимает дату и диапазон ('W', 'M', 'Y', 'ALL').
    Возвращает JSON с расходами, поступлениями, курсами, акциями.
    """
    # 1. Загружаем данные
    transactions = load_excel(XLSX_FILE)
    settings = load_user_settings()

    # 2. Определяем диапазон дат

    dt = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d")
    end_date = dt.strftime("%Y-%m-%d 23:59:59")

    if range_type == 'W':
        # Неделя (с понедельника)
        start_date = (dt - datetime.timedelta(days=dt.weekday())).strftime("%Y-%m-%d 00:00:00")
    elif range_type == 'Y':
        # Год (с 1 января)
        start_date = dt.replace(month=1, day=1).strftime("%Y-%m-%d 00:00:00")
    elif range_type == 'ALL':
        # Все данные до указанной даты
        start_date = "2000-01-01 00:00:00"
    else:  # 'M' по умолчанию
        # Месяц (с 1 числа)
        start_date = dt.replace(day=1).strftime("%Y-%m-%d 00:00:00")

    filtered_data = _filter_by_date(transactions, start_date, end_date)

    # 3. Получаем доходы/расходы
    stats = get_income_expense(filtered_data)

    # 4. Форматируем расходы
    expense_cat = stats["expense"]["categories"]
    # Сортируем по убыванию
    sorted_exp = sorted(expense_cat.items(), key=lambda x: x[1], reverse=True)

    # Выделяем Переводы и Наличные отдельно
    transfers_and_cash = []
    main_expenses = []

    for cat, amount in sorted_exp:
        if cat in ["Переводы", "Наличные"]:
            transfers_and_cash.append({"category": cat, "amount": round(amount)})
        else:
            main_expenses.append({"category": cat, "amount": round(amount)})

    # Оставляем топ-7 основных, остальное в "Остальное"
    top_7 = main_expenses[:7]
    rest = main_expenses[7:]
    if rest:
        rest_sum = sum(item["amount"] for item in rest)
        top_7.append({"category": "Остальное", "amount": rest_sum})

    # Сортируем Переводы и Наличные по убыванию
    transfers_and_cash.sort(key=lambda x: x["amount"], reverse=True)

    # 5. Форматируем доходы
    income_cat = stats["income"]["categories"]
    sorted_inc = sorted(income_cat.items(), key=lambda x: x[1], reverse=True)
    income_main = [{"category": cat, "amount": round(amount)} for cat, amount in sorted_inc]

    # 6. Валюты и акции
    raw_rates = get_currency_rates(settings.get("user_currencies", []))
    currency_rates = [{"currency": k, "rate": v} for k, v in raw_rates.items()]

    raw_stocks = get_stock_prices(settings.get("user_stocks", []))
    stock_prices = [{"stock": k, "price": v} for k, v in raw_stocks.items()]

    # 7. Формируем итоговый JSON
    return {
        "expenses": {
            "total_amount": round(stats["expense"]["total"]),
            "main": top_7,
            "transfers_and_cash": transfers_and_cash
        },
        "income": {
            "total_amount": round(stats["income"]["total"]),
            "main": income_main
        },
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }


if __name__ == "__main__":
    # Тестируем Главную страницу
    print("--- ГЛАВНАЯ СТРАНИЦА ---")
    import json

    main_json = generate_main_page("2021-12-31 15:30:00")
    print(json.dumps(main_json, ensure_ascii=False, indent=2))

    print("\n--- СТРАНИЦА СОБЫТИЙ (Месяц) ---")
    events_json = generate_events_page("2021-12-31", 'M')
    print(json.dumps(events_json, ensure_ascii=False, indent=2))