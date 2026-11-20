import json
from pathlib import Path
import logging

logger = logging.getLogger("sheetbridge")

# Строим путь до корня проекта: configs.py -> services -> src -> SheetBridge
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_SETTINGS = BASE_DIR / "configs" / "user_settings.json"

def load_user_settings(settings_path: str = None) -> dict:
        """
        Загружает настройки пользователя из JSON-файла.

        Аргументы:
            settings_path: опциональный путь к файлу.
                           Если не указан, берется configs/user_settings.json.

        Возвращает:
            Словарь с настройками. Если файл не найден или поврежден,
            возвращает словарь с пустыми списками.
        """
        # Если путь передан — используем его, иначе берем стандартный
        path = Path(settings_path) if settings_path else DEFAULT_SETTINGS

        try:
            # Читаем текст из файла (явно указываем utf-8 для Windows)
            content = path.read_text(encoding="utf-8")
            # Превращаем строку JSON в словарь Python
            data = json.loads(content)

        except FileNotFoundError:
            # Если файла нет — не падаем, а возвращаем пустые списки
            logger.warning(f"Файл настроек не найден: {path}. Используются пустые списки.")
            return {"user_currencies": [], "user_stocks": []}

        except json.JSONDecodeError as e:
            # Если файл есть, но внутри ошибка (например, забыли запятую)
            logger.error(f"Ошибка парсинга JSON в файле {path}: {e}")
            return {"user_currencies": [], "user_stocks": []}

        # На всякий случай проверяем, что нужные ключи вообще есть.
        # Если пользователь удалил их из файла, setdefault добавит пустые списки.
        data.setdefault("user_currencies", [])
        data.setdefault("user_stocks", [])

        return data

    # Блок для быстрой проверки (сработает, если запустить файл напрямую)
if __name__ == "__main__":
    print("Путь к настройкам:", DEFAULT_SETTINGS)
    print("Файл существует:", DEFAULT_SETTINGS.exists())
    print("Результат загрузки:", load_user_settings())