from pathlib import Path

import pandas as pd

# Определил путь до файла с операциями по счету/карте
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_PATH = DATA_DIR / "input"
XLSX_FILE = DATA_PATH / "operations.xlsx"




def load_excel(file_path: str, config: dict = None) -> list[dict]:
    """
    Читает путь к файлу.
    Excel-файл полученный из директории data/input/operations.xlsx.
    Возвращает список словарей транзакций.
    config – словарь с маппингом колонок.
    Аргументы:
        file_path: путь к Excel-файлу
        config: словарь маппинга колонок вида:
            {
                "date": "Реальное имя колонки с датой",
                "amount": "Реальное имя колонки с суммой",
                "description": "Реальное имя колонки с описанием",
                "category": "Реальное имя колонки с категорией",
                "card": "Реальное имя колонки с номером карты"
            }
            Если не передан, используется стандартный маппинг.

    Возвращает:
        Список словарей с ключами: date, amount, description, category, card_number
    """
    # 1. Стандартный словарь операций
    default_config = {
        "date": "дата операции",
        "amount": "сумма операции",
        "description": "описание",
        "category": "категория",
        "card": "номер карты"
    }
    # 2. Если конфиг передали, то обновляем на новые данные.
    if config:
        default_config.update(config)
    mapping = default_config

    try:
        # Дата-фрейм получили, колонки тоже, теперь надо отсортировать по дате.
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return []
    # 3. Привел все колонки к нижнему регистру.
    df.columns = df.columns.str.lower().str.strip()

    # 4. Проверяю наличие обязательных колонок.
    required = ["date", "amount", "description"]
    for key in required:
        col_name = mapping.get(key)
        if col_name not in df.columns:
            print(f"Ошибка: колонка '{col_name}' (для поля '{key}') не найдена в файле.")
            return []
    # 5. Преобразую колонку с датой в datetime и сортирую.
    data_col = mapping['date']
    # Преобразую Дата-фрейм колонки дата к datetime формату, чтобы сортировать строки с некорректной датой.
    df[data_col] = pd.to_datetime(df[data_col], errors='coerce', format="%d.%m.%Y %H:%M:%S")
    # Выбрасываю все некорректные даты (NaT)
    df = df.dropna(subset=[data_col])
    # Сортирую даты
    df = df.sort_values(by=data_col)

    # 6. Формирую итоговый список словарей
    result = []
    amount_col = mapping["amount"]
    desc_col = mapping["description"]
    cat_col = mapping.get("category")
    card_col = mapping.get("card")

    for _, row in df.iterrows():
        valid_date = row[data_col]
        if pd.isna(valid_date):
            continue
        date_str = valid_date.strftime("%Y-%m-%d %H:%M:%S")

        # Сумма преобразую в float если это возможно.
        try:
            amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0.0
        except (TypeError, ValueError):
            amount = 0.0

        # Описание
        try:
            description = str(row[desc_col]) if pd.notna(row[desc_col]) else ""
        except (TypeError, ValueError):
            description = ""

        # Категория (если колонка есть, иначе "Неизвестно")
        if cat_col and cat_col in df.columns and pd.notna(row[cat_col]):
            category = str(row[cat_col])
        else:
            category = "Неизвестно"

        # Номер карты (последние 4 цифры если есть)
        if card_col and card_col in df.columns and pd.notna(row[card_col]):
            card_number = str(row[card_col]).strip()
            if len(card_number) >= 4:
                card_number = card_number[-4:]
        else:
            card_number = ""



        transaction = {
            "date": date_str,
            "amount": amount,
            "description": description,
            "category": category,
            "card_number": card_number,

        }
        # Добавляю все словари в итоговый список
        result.append(transaction)

    return result


