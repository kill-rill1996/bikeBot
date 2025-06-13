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
