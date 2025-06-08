import calendar
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


def convert_str_to_datetime(date_str: str) -> datetime.datetime:
    """Перевод из строки в datetime. Необходима строка формата d.m.y"""
    return datetime.datetime.strptime(date_str, "%d.%m.%Y")


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

    # кастомный период в формате custom-{start_date}-{end_date}
    # TODO нужно ли
    else:
        end_period = convert_str_to_datetime(period.split("-")[1])
        start_period = convert_str_to_datetime(period.split("-")[2])

    return (start_period, end_period)


def get_days_in_month(year: int, month: int) -> list[datetime.date]:
    """Возвращает список всех дней в заданном месяце датами"""
    # количество дней в месяце
    _, num_days = calendar.monthrange(year, month)

    start_date = datetime.date(year, month, 1)
    all_days = []
    for i in range(num_days):
        all_days.append(start_date + datetime.timedelta(days=i))

    return all_days


def get_next_and_prev_month_and_year(month: int, year: int) -> dict:
    """Расчет следующего и предыдущего месяцев и года"""
    result = {}
    if month == 1:
        result["prev_month"] = 12
        result["next_month"] = 2
        result["prev_year"] = year - 1
        result["next_year"] = year
    elif month == 12:
        result["prev_month"] = 11
        result["next_month"] = 1
        result["prev_year"] = year
        result["next_year"] = year + 1
    else:
        result["prev_month"] = month - 1
        result["next_month"] = month + 1
        result["prev_year"] = year
        result["next_year"] = year

    return result
