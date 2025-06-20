import datetime
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from schemas.users import User


def mechanic_report_graphic(durations_by_dates: dict, y_1: list, y_2: list, x, mechanic: User,
                            start_date: datetime.datetime, end_date: datetime.datetime) -> str:
    """Строит и сохраняет график в папку, возвращает место расположение графика"""

    # Настройка графика
    plt.xticks(rotation=0, fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Устанавливаем лимиты по y от 0 до максимального кол-ва времени + запас 10%
    plt.ylim(0, max([value[1] for value in durations_by_dates.values()]) * 1.1)

    x_positions = np.arange(len(x))  # позиции по оси X
    width = 0.35  # ширина столбца
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x_positions - width / 2, y_1, width, label='Суммарное время выполнения работ')
    rects2 = ax.bar(x_positions + width / 2, y_2, width, label='Кол-во выполненных работ')

    # добавляем подписи значений
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # смещение текста вверх
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    # добавляем линию среднего значения времени выполнения работ
    mean_value = sum([value[0] for value in durations_by_dates.values()]) / len(x)
    plt.axhline(y=mean_value, color='red',
                linestyle='--', label=f'Среднее время: {mean_value:.2f}')
    plt.legend()

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x)
    ax.set_xlabel('Дата')  # Подпись оси X
    ax.set_ylabel('Время, в мин. / Кол-во выполненных работ')  # Подпись оси Y
    ax.set_title(f"Отчет по механику {mechanic.username} {start_date.date()} - {end_date.date()}", fontsize=14)
    ax.legend()

    # Путь для сохранения графика
    chart_path = f"reports/graphics/mechanic_report_{mechanic.id}_{start_date.date()}-{end_date.date()}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


def all_mechanics_report_graphic(data: dict[str:tuple], start_date: datetime.datetime, end_date: datetime.datetime):
    """График по всем механикам"""
    # Сортируем данные
    sorted_data_list = sorted(data.items(), key=lambda item: item[1][0])

    x_label = []
    y_values1 = []
    y_values2 = []

    # Делаем выборку для значений осей
    for mechanic in sorted_data_list:
        x_label.append(mechanic[0])
        y_values1.append(mechanic[1][0])
        y_values2.append(mechanic[1][1])

    # Настройка графика
    plt.xticks(rotation=0, fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    x = np.arange(len(x_label))  # позиции по оси X
    width = 0.35  # ширина столбца

    fig, ax = plt.subplots()
    bars1 = ax.bar(x - width / 2, y_values1, width, label='Затраченное время', color='deepskyblue')
    bars2 = ax.bar(x + width / 2, y_values2, width, label='Кол-во выполненных операций', color='orange')

    def add_autolabel(one_bar: Any) -> None:
        for bar in one_bar:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # смещение по y
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Добавляем подписи значений над каждым столбцом
    for bar in [bars1, bars2]:
        add_autolabel(bar)

    # Подписываем оси
    ax.set_xlabel('Механики', fontsize=10)
    ax.set_ylabel('Время, в мин. / Кол-во выполненных работ', fontsize=10)
    ax.set_title(f'Отчет по механикам {start_date.date()} - {end_date.date()}', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(x_label)
    ax.legend(fontsize=8)

    # Путь для сохранения графика
    chart_path = f"reports/graphics/graphic_mechanics_{start_date.date()}_{end_date.date()}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


def location_graphic_report(data: dict, start_date: str, end_date: str, location: str) -> str:
    """График по местоположению"""
    from datetime import datetime, timedelta

    def parse_date(date_str):
        return datetime.strptime(date_str, '%d.%m.%Y')

    def format_date(date_obj):
        return date_obj.strftime('%d.%m.%Y')

    # Собираем все уникальные типы транспорта
    all_types = set()
    for values in data.values():
        all_types.update(values.keys())
    all_types = sorted(all_types)

    # Генерируем все даты в диапазоне
    start = parse_date(start_date)
    end = parse_date(end_date)
    num_days = (end - start).days + 1
    all_dates = [format_date(start + timedelta(days=i)) for i in range(num_days)]

    # Для каждого типа транспорта собираем значения по всем датам диапазона
    values_by_type = []
    for t in all_types:
        values = []
        for d in all_dates:
            values.append(data.get(d, {}).get(t, 0))
        values_by_type.append(values)

    x = np.arange(len(all_dates))
    width = 0.8 / len(all_types)

    fig, ax = plt.subplots(figsize=(max(8, len(all_dates) * 1.2), 5))
    colors = ['deepskyblue', 'orange', 'green', 'red', 'purple', 'brown', 'gray']

    bar_containers = []
    for i, (t, values) in enumerate(zip(all_types, values_by_type)):
        bars = ax.bar(
            x + (i - len(all_types) / 2) * width + width / 2,
            values,
            width,
            label=t,
            color=colors[i % len(colors)]
        )
        bar_containers.append(bars)

    # Добавляем подписи значений над каждым баром
    for bars in bar_containers:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=9
                )

    ax.set_xlabel('Дата')
    ax.set_ylabel('Количество')
    ax.set_title(f'Кол-во транспорта в \"{location}\" {start_date} - {end_date}')
    ax.set_xticks(x)
    ax.set_xticklabels(all_dates, rotation=45)
    ax.legend(fontsize=10)

    # Путь для сохранения графика
    chart_path = f"reports/graphics/location_{location}_{start_date}-{end_date}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


def transport_by_category_graphic_report(jobs_count_by_dates: dict, y: list, x: list, category_title: str,
                            start_date: datetime.datetime, end_date: datetime.datetime) -> str:
    """График по категории транспорта"""
    # Настройка графика
    plt.xticks(rotation=0, fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Устанавливаем лимиты по y от 0 до максимального кол-ва времени + запас 10%
    plt.ylim(0, max([value for value in jobs_count_by_dates.values()]) * 1.1)

    x_positions = np.arange(len(x))  # позиции по оси X
    width = 0.35  # ширина столбца
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x_positions + width / 2, y, width, label='Кол-во выполненных работ')

    # добавляем подписи значений
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3),
                        # смещение текста вверх
                        textcoords="offset points", ha='center', va='bottom')

    autolabel(rects1)

    # добавляем линию среднего значения количества работ
    mean_value = sum([value for value in jobs_count_by_dates.values()]) / len(x)
    plt.axhline(y=mean_value, color='red', linestyle='--', label=f'Среднее количество работ: {mean_value:.2f}')
    plt.legend()

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x)
    ax.set_xlabel('Дата')  # Подпись оси X
    ax.set_ylabel('Кол-во выполненных работ')  # Подпись оси Y
    ax.set_title(f"Отчет по категории транспорта {category_title} {start_date.date()} - {end_date.date()}", fontsize=14)
    ax.legend()

    # Путь для сохранения графика
    chart_path = f"reports/graphics/transport_report_{category_title}_{start_date.date()}-{end_date.date()}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


def transport_by_subcategory_graphic_report(jobs_count_by_dates: dict, y: list, x: list, subcategory_title: str,
                            start_date: datetime.datetime, end_date: datetime.datetime) -> str:
    """График по подкатегории транспорта"""
    # Настройка графика
    plt.xticks(rotation=0, fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Устанавливаем лимиты по y от 0 до максимального кол-ва времени + запас 10%
    plt.ylim(0, max([value for value in jobs_count_by_dates.values()]) * 1.1)

    x_positions = np.arange(len(x))  # позиции по оси X
    width = 0.35  # ширина столбца
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x_positions + width / 2, y, width, label='Кол-во выполненных работ')

    # добавляем подписи значений
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3),
                        # смещение текста вверх
                        textcoords="offset points", ha='center', va='bottom')

    autolabel(rects1)

    # добавляем линию среднего значения количества работ
    mean_value = sum([value for value in jobs_count_by_dates.values()]) / len(x)
    plt.axhline(y=mean_value, color='red', linestyle='--', label=f'Среднее количество работ: {mean_value:.2f}')
    plt.legend()

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x)
    ax.set_xlabel('Дата')  # Подпись оси X
    ax.set_ylabel('Кол-во выполненных работ')  # Подпись оси Y
    ax.set_title(f"Отчет по подкатегории транспорта {subcategory_title} {start_date.date()} - {end_date.date()}", fontsize=14)
    ax.legend()

    # Путь для сохранения графика
    chart_path = f"reports/graphics/transport_report_{subcategory_title}_{start_date.date()}-{end_date.date()}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


def transport_by_transport_graphic_report(jobs_count_by_dates: dict, y: list, x: list, transport_title: str,
                            start_date: datetime.datetime, end_date: datetime.datetime) -> str:
    """График по транспорту"""
    # Настройка графика
    plt.xticks(rotation=0, fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Устанавливаем лимиты по y от 0 до максимального кол-ва времени + запас 10%
    plt.ylim(0, max([value for value in jobs_count_by_dates.values()]) * 1.1)

    x_positions = np.arange(len(x))  # позиции по оси X
    width = 0.35  # ширина столбца
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x_positions + width / 2, y, width, label='Кол-во выполненных работ')

    # добавляем подписи значений
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3),
                        # смещение текста вверх
                        textcoords="offset points", ha='center', va='bottom')

    autolabel(rects1)

    # добавляем линию среднего значения количества работ
    mean_value = sum([value for value in jobs_count_by_dates.values()]) / len(x)
    plt.axhline(y=mean_value, color='red', linestyle='--', label=f'Среднее количество работ: {mean_value:.2f}')
    plt.legend()

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x)
    ax.set_xlabel('Дата')  # Подпись оси X
    ax.set_ylabel('Кол-во выполненных работ')  # Подпись оси Y
    ax.set_title(f"Отчет по транспорту {transport_title} {start_date.date()} - {end_date.date()}", fontsize=14)
    ax.legend()

    # Путь для сохранения графика
    chart_path = f"reports/graphics/transport_report_{transport_title}_{start_date.date()}-{end_date.date()}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


def jobtypes_for_category_graphic(data: dict, category_id: int, category_title: str,
                                  start_date: datetime.datetime, end_date: datetime.datetime) -> str:
    """Строит график для выбранных групп узлов и категории за определенный период"""
    from datetime import datetime
    # Получаем все даты и категории
    dates = list(data.keys())
    all_categories = set()
    for cats in data.values():
        all_categories.update(cats.keys())
    all_categories = sorted(all_categories)

    x = np.arange(len(dates))  # позиции по оси X

    # Форматируем даты для подписи
    dates_formatted = [
        datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y") for date in dates
    ]

    # Готовим значения для каждой категории по всем датам
    category_values = []
    for cat in all_categories:
        values = []
        for date in dates:
            values.append(data[date].get(cat, 0))
        category_values.append(values)

    width = 0.12  # ширина одного столбца
    fig, ax = plt.subplots(figsize=(12, 6))

    # Строим bar-графики для каждой категории
    for i, (cat, values) in enumerate(zip(all_categories, category_values)):
        bars = ax.bar(x + i * width, values, width, label=cat)
        # Добавляем подписи над каждым столбцом
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # смещение вверх
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Дата')
    ax.set_ylabel('Количество вып. операций')
    start_date_str = start_date.date().strftime("%d.%m.%Y")
    end_date_str = end_date.date().strftime("%d.%m.%Y")
    ax.set_title(f'Категория {category_title} {start_date_str}-{end_date_str}')
    ax.set_xticks(x + width * (len(all_categories) - 1) / 2)
    ax.set_xticklabels(dates_formatted, rotation=45)
    ax.legend()

    # Путь для сохранения графика
    chart_path = f"reports/graphics/work_category_{category_id}_{start_date_str}-{end_date_str}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


def inefficiency_graphic(data, dates_period: list[str], threshold: int) -> str | None:
    """
    Строит группированный bar-график:
    по оси X — даты,
    по каждой дате — бары для каждой работы,
    учитываются только работы, у которых суммарное количество за все даты > threshold.
    Над каждым bar — подпись значения.
    """
    # Сортируем даты
    dates = sorted(data.keys(), key=lambda d: [int(x) for x in d.split('.')][::-1])

    # Считаем суммарное количество каждой работы за все даты
    job_total_counts = {}
    for jobs in data.values():
        for job, count in jobs.items():
            job_total_counts[job] = job_total_counts.get(job, 0) + count

    # Оставляем только работы, у которых суммарное количество > threshold
    all_jobs = [job for job, total in job_total_counts.items() if total >= threshold]
    all_jobs = sorted(all_jobs)

    if not all_jobs:
        return None

    # Формируем матрицу: строки — работы, столбцы — даты
    job_counts = []
    for job in all_jobs:
        job_counts.append([data[date].get(job, 0) for date in dates])

    # Построение grouped bar chart
    x = np.arange(len(dates))
    width = 0.8 / len(all_jobs)  # ширина одного бара

    plt.figure(figsize=(max(12, len(dates)), 6))
    bars = []
    for i, job in enumerate(all_jobs):
        bar = plt.bar(x + i * width, job_counts[i], width, label=job)
        bars.append(bar)
        # Добавляем подписи над каждым bar
        for rect, value in zip(bar, job_counts[i]):
            if value > 0:
                plt.text(
                    rect.get_x() + rect.get_width() / 2,
                    rect.get_height(),
                    str(value),
                    ha='center',
                    va='bottom',
                    fontsize=9
                )

    plt.ylabel("Количество работ")
    plt.xlabel("Дата")
    plt.title(f"Неэффективность >= {threshold} работ {dates_period[0]} - {dates_period[-1]}")
    plt.xticks(x + width * (len(all_jobs) - 1) / 2, dates, rotation=45, ha='right')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Путь для сохранения графика
    chart_path = f"reports/graphics/inefficiency_{dates_period[0]}_{dates_period[-1]}.png"

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path
