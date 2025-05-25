from datetime import datetime
import pytz

from settings import settings


def convert_date_time(date: datetime, with_tz: bool = None) -> (str, str):
    """Перевод даты в формат для вывода"""
    # перевод в текущий часовой пояс
    if with_tz:
        date = date.astimezone(tz=pytz.timezone(settings.timezone))
        return date.date().strftime("%d.%m.%Y"), date.time().strftime("%H:%M")

    return date.date().strftime("%d.%m.%Y"), date.time().strftime("%H:%M")