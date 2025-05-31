import datetime
import pytz

from settings import settings


def convert_date_time(date: datetime.datetime, with_tz: bool = None) -> (str, str):
    """Перевод даты в формат для вывода (date, time)"""
    # перевод в текущий часовой пояс
    if with_tz:
        date = date.astimezone(tz=pytz.timezone(settings.timezone))
        return date.date().strftime("%d.%m.%Y"), date.time().strftime("%H:%M")

    return date.date().strftime("%d.%m.%Y"), date.time().strftime("%H:%M")


def get_dates_by_period(period: str) -> (datetime.datetime, datetime.datetime):
    """Возвращает (start_date, end_date) для запрашиваемого периода"""
    if period == "today":
        start_period = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:01", "%Y-%m-%d %H:%M:%S"
        )
        end_period = datetime.datetime.now()

    elif period == "yesterday":
        start_period = datetime.datetime.strptime(
            (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 00:00:01",
            "%Y-%m-%d %H:%M:%S"
        )
        end_period = datetime.datetime.strptime(start_period.strftime("%Y-%m-%d") + " 23:59:59", "%Y-%m-%d %H:%M:%S")

    elif period == "week":
        end_period = datetime.datetime.now()
        start_period = end_period - datetime.timedelta(days=7)

    elif period == "month":
        end_period = datetime.datetime.now()
        start_period = end_period - datetime.timedelta(days=30)  # ставим для месяца 30 дней

    return (start_period, end_period)