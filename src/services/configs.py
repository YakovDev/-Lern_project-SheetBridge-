def load_user_settings(settings_path: str = "configs/user_settings.json") -> dict:
    """
    Загружает пользовательские настройки (валюты, акции, порог округления).
    Возвращает словарь с ключами 'user_currencies', 'user_stocks', 'round_limit'.
    """