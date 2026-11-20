import json
import re
from pathlib import Path
import pandas as pd
import math
import requests
import logging

logger = logging.getLogger("sheetbridge")




def get_card_summary(transactions: list[dict]) -> dict:
    """
    Группирует расходы по картам (последние 4 цифры).
    Возвращает {"1234": {"spent": 1000.0, "cashback": 10.0}, ... }.
    """
    accumulator = {}
    result = {}
    if transactions:
        for t in transactions:
            amount = t.get("amount")
            card = t.get("card_number")
            if amount < 0:
                spent = abs(amount)
                if card not in accumulator:
                    accumulator[card] = spent
                else:
                    accumulator[card] += spent
        for card, spent in accumulator.items():
            total_spent = spent
            cashback = total_spent / 100
            rounded_cashback = round(cashback, 2)
            rounded_spent = round(total_spent, 2)
            result[card] = {"spent": rounded_spent, "cashback": rounded_cashback}

    return result





def get_top_transactions(transactions: list[dict], n: int = 5) -> list[dict]:
    """Возвращает топ-N транзакций по сумме расхода."""
    # Собираю все транзакции расходов
    expenses = [t for t in transactions if t["amount"] < 0]
    # Сортирую полученный список
    result = sorted(expenses, key=lambda a: a["amount"], reverse=False)[:n]
    return result


def get_category_spending(transactions: list[dict], top_n: int = 7) -> dict:
    """
    Группирует расходы по категориям. Топ-N категорий + категория "Остальное".
    Возвращает {"Категория": сумма, ...}.
    """
    category_totals = {}
    for t in transactions:
        if t["amount"] < 0:
            cat = t.get("category") or "Неизвестно"
            spent = abs(t["amount"])

            if cat in category_totals:
                category_totals[cat] += spent  # прибавить к существующему
            else:
                category_totals[cat] = spent  # создать новый ключ
    sorted_spent = sorted(category_totals.items(), key=lambda a: a[1], reverse=True)

    top_categories = sorted_spent[:top_n]  # беру первые top_n категорий
    top_dict = dict(top_categories)
    # Всё, что осталось суммирую в «Остальное»
    rest = sorted_spent[top_n:]

    rest_sum = sum(amount for _, amount in rest)
    result = top_dict
    if rest_sum > 0:
        result["Остальное"] = rest_sum

    return result

def get_income_expense(transactions: list[dict]) -> dict:
    """
    Считает общие суммы доходов и расходов, разбивает по категориям.
    Возвращает {'income': {'total': float, 'categories': {...}},
               'expense': {'total': float, 'categories': {...}}}
    """

    result = {}
    income = [t for t in transactions if t["amount"] > 0]
    expenses = [t for t in transactions if t["amount"] < 0]
    expense_categories = {}
    income_categories = {}
    for t in expenses:
        cat = t.get("category") or "Неизвестно"
        spent = abs(t["amount"])
        expense_categories[cat] = expense_categories.get(cat, 0) + spent
    total_expense = sum(expense_categories.values())
    result["expense"] = {"total": total_expense, "categories": expense_categories}

    for t in income:
        cat = t.get("category") or "Неизвестно"
        amount = t["amount"]
        income_categories[cat] = income_categories.get(cat, 0) + amount
    total_income = sum(income_categories.values())
    result["income"] = {"total": total_income, "categories": income_categories}

    return result


def filter_by_phone(transactions: list[dict]) -> list[dict]:
    """Возвращает транзакции, в описании которых есть номер телефона (регулярка)."""
    pattern = re.compile(r"(?:\+7|8)\s?\(?\d{3}\)?\s?\d{2,3}[- ]?\d{2}[- ]?\d{2}")
    result = []
    for t in transactions:
        desc = t.get("description") or ""
        if pattern.search(desc):
            result.append(t)

    return result







def filter_transfers_to_individuals(transactions: list[dict]) -> list[dict]:
    """Возвращает переводы физлицам (категория 'Переводы' + описание вида 'Имя Ф.')."""
    result = []
    pattern = re.compile(r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.")
    for t in transactions:
        if t.get("category") != "Переводы":
            continue
        desc = t.get("description") or ""
        if pattern.search(desc):
            result.append(t)
    return result



# ------------------------------------------------------------
# Экспорт и внешние API
# ------------------------------------------------------------
def export_to_json(data: dict, file_path: str) -> None:
    """Сохраняет словарь в JSON-файл."""

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def export_to_excel(data: dict, file_path: str, template: str = None) -> None:
    """
    Генерирует Excel-отчёт из словаря.

    Поддерживает три случая:
    1. Плоский словарь {ключ: число} — один лист.
    2. Вложенный {карта: {spent, cashback}} — один лист с колонками.
    3. Вложенный {секция: {total, categories}} — несколько листов.

    Аргументы:
        data: словарь с данными.
        file_path: путь к .xlsx файлу.
        template: опциональный шаблон (пока не используется).
    """
    # 1. Создаю папку, если её нет
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 2. Пустой словарь — создаю пустой файл с сообщением
    if not data:
        df = pd.DataFrame({"Сообщение": ["Нет данных для отчёта"]})
        df.to_excel(file_path, index=False, engine="openpyxl")
        return

    # 3. Тип данных
    values = list(data.values())
    all_dicts = all(isinstance(v, dict) for v in values)

    # 4. {категория: сумма}
    if not all_dicts:
        df = pd.DataFrame(list(data.items()), columns=["Ключ", "Значение"])
        df.to_excel(file_path, index=False, engine="openpyxl")
        return

    # 5. Вложенный случай что внутри
    first_value = values[0]

    # 5a. {карта: {spent, cashback}} — get_card_summary
    if "spent" in first_value and "cashback" in first_value:
        rows = [
            {
                "Карта": card,
                "Потрачено": info["spent"],
                "Кешбэк": info["cashback"],
            }
            for card, info in data.items()
        ]
        df = pd.DataFrame(rows)
        df.to_excel(file_path, index=False, engine="openpyxl")
        return

    #  {секция: {total, categories}} — get_income_expense

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        for section_name, section_data in data.items():
            # Имя листа <= 31 символа, без запрещённых символов
            sheet_name = str(section_name)[:31]

            # Если внутри есть "categories" беру его
            if isinstance(section_data, dict) and "categories" in section_data:
                inner = section_data["categories"]
            elif isinstance(section_data, dict):
                inner = section_data


            df = pd.DataFrame(list(inner.items()), columns=["Ключ", "Значение"])
            df.to_excel(writer, sheet_name=sheet_name, index=False)








# ------------------------------------------------------------
# Сервисы из ТЗ (поиск)
# ------------------------------------------------------------


def search_transactions(query: str, transactions: list[dict]) -> list[dict]:
    """Возвращает транзакции, содержащие query в описании или категории."""
    results = []
    query_lower = query.lower()
    for t in transactions:
        desc = (t.get("description") or "").lower()
        cat = (t.get("category") or "").lower()
        if query_lower in desc or query_lower in cat:
            results.append(t)
    return results


# ------------------------------------------------------------
# Внешние API
# ------------------------------------------------------------
def get_currency_rates(currencies: list[str]) -> dict:
    """Возвращает текущие курсы валют (к рублю) через внешнее API."""
    url = "https://open.er-api.com/v6/latest/RUB"
    result = {}
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        rates = response.json().get("rates", {})

        for currency in currencies:
            if currency in rates and rates[currency] != 0:
                # Инвертируем курс, чтобы получить стоимость 1 валюты в рублях
                rub_rate = 1 / rates[currency]
                result[currency] = round(rub_rate, 2)
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
    return result


def get_stock_prices(stocks: list[str]) -> dict:
    """Возвращает текущие цены акций через Yahoo Finance (chart API).
    :rtype: dict
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
    }
    result = {}

    for ticker in stocks:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Достаём цену из структуры ответа
            chart = data.get("chart", {}).get("result")
            if chart:
                meta = chart[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                if price is not None:
                    result[ticker] = round(price, 2)
        except Exception as e:
            logger.error(f"Ошибка получения цены {ticker}: {e}")

    return result


# ------------------------------------------------------------
# Сервисы из ТЗ (анализ кешбэка, инвесткопилка)
# ------------------------------------------------------------
def cashback_analysis(data: list[dict], year: int, month: int) -> list[dict]:
    """
    Анализирует выгодные категории повышенного кешбэка.
    Возвращает список словарей, отсортированный по убыванию кешбэка.
    """
    category_spending = {}
    for t in data:
        if t["amount"] < 0:
            date_str = t.get("date", "")
            try:
                t_year = int(date_str[:4])
                t_month = int(date_str[5:7])
            except (ValueError, IndexError):
                continue
            if t_year == year and t_month == month:
                cat = t.get("category") or "Неизвестно"
                spent = abs(t["amount"])
                category_spending[cat] = category_spending.get(cat, 0) + spent

    # Считаем 1% кешбэка
    result = []
    for cat, spent in category_spending.items():
        result.append({"category": cat, "cashback": round(spent / 100, 2)})

    # Сортируем по убыванию кешбэка и берем топ-3 (или все, если их меньше)
    result.sort(key=lambda x: x["cashback"], reverse=True)
    return result[:3]


def investment_bank(month: str, transactions: list[dict], limit: int) -> float:
    """
    Рассчитывает накопления по правилу «Инвесткопилка» за указанный месяц.
    month – 'YYYY-MM'.
    limit – шаг округления (10, 50, 100).
    """
    total_saved = 0.0

    for t in transactions:
        if t["amount"] < 0:  # Только расходы
            date_str = t.get("date", "")
            if date_str[:7] == month:  # Отсекаем всё, что не попадает в месяц
                spent = abs(t["amount"])

                # Округляем ВВЕРХ до кратного limit
                # Например: 1712 -> 1750 (при limit 50)
                rounded = math.ceil(spent / limit) * limit

                # Разница идет в копилку
                diff = rounded - spent
                total_saved += diff

    return round(total_saved, 2)


