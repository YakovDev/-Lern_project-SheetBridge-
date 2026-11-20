import pytest
import pandas as pd
from src.services.loader import load_excel

def test_load_excel_success(tmp_path):
    # 1. Создаем временный Excel-файл
    test_file = tmp_path / "test_operations.xlsx"
    df = pd.DataFrame({
        "Дата операции": ["01.12.2021 10:00:00", "02.12.2021 11:00:00"],
        "Сумма операции": [-1000.0, 500.0],
        "Описание": ["Магнит", "Зарплата"],
        "Категория": ["Супермаркеты", "Пополнения"],
        "Номер карты": ["*1111", ""]
    })
    df.to_excel(test_file, index=False)

    # 2. Вызываем функцию
    result = load_excel(str(test_file))

    # 3. Проверяем результат
    assert len(result) == 2
    assert result[0]["amount"] == -1000.0
    assert result[0]["category"] == "Супермаркеты"
    assert result[0]["card_number"] == "1111" # должны отброситься символы *
    assert result[1]["amount"] == 500.0

def test_load_excel_file_not_found():
    # Проверяем, что при отсутствии файла возвращается пустой список
    result = load_excel("non_existent_file.xlsx")
    assert result == []