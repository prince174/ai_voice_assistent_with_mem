import logging
import sys
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/bot.log",
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
):
    """Настройка логирования для всего приложения"""
    
    # Создаем папку для логов если её нет
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Форматтер
    formatter = logging.Formatter(format_string)
    
    # Хендлер для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Уменьшаем шум от некоторых библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
    
    logging.info("✅ Логирование настроено")

def get_logger(name: str) -> logging.Logger:
    """Получить логгер для модуля"""
    return logging.getLogger(name)