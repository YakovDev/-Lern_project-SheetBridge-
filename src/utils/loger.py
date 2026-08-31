import logging

def setup_logger(name: str = "sheetbridge", log_file: str = "logs/sheetbridge.log") -> logging.Logger:
    """Настраивает и возвращает логгер с выводом в файл и консоль."""