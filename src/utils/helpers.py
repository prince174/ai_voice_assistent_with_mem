import json
from typing import Any, Dict
from datetime import datetime

def format_timestamp(dt: datetime = None) -> str:
    """Форматирует timestamp для логов"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """Обрезает текст для логов"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def safe_json_loads(data: str) -> Dict[str, Any]:
    """Безопасная загрузка JSON"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return {}

def format_size(size_bytes: int) -> str:
    """Форматирует размер файла в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"