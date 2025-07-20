# utils/timezones.py
from datetime import datetime, timedelta

def get_current_time() -> datetime:
    """Возвращает объект datetime с учётом Киевского времени (UTC+3)."""
    return datetime.utcnow() + timedelta(hours=3)