import json
from src.services.configs import load_user_settings

def test_load_user_settings_success(tmp_path):
    # Создаем временный JSON
    test_file = tmp_path / "settings.json"
    test_data = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    test_file.write_text(json.dumps(test_data), encoding="utf-8")

    result = load_user_settings(str(test_file))
    assert result["user_currencies"] == ["USD"]
    assert result["user_stocks"] == ["AAPL"]

def test_load_user_settings_missing_file():
    # Если файла нет, должны вернуться пустые списки (чтобы программа не упала)
    result = load_user_settings("non_existent.json")
    assert result == {"user_currencies": [], "user_stocks": []}